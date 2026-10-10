/* GENERATED FILE - do not edit by hand.
   Source: content/deepdive/   Build: python3 build.py
   Every code block below was executed and its output captured. */

window.GRAIL_DEEP = [
  {
    "id": "gil",
    "title": "The Global Interpreter Lock",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "The GIL is the single most-cited reason Python &ldquo;can&rsquo;t do threads&rdquo;, and most of what people say about it is half right. It does not stop you using threads, it does not make your code thread-safe, and it does not slow down I/O-bound programs. What it does is stop two threads from executing Python bytecode <em>at the same instant</em> inside one interpreter &mdash; which is exactly the thing a CPU-bound program needs.",
      "This page builds the model from the bottom up: what the lock protects, when it is released, why that makes I/O-bound threading fine and CPU-bound threading useless, why you still need your own locks, and what the alternatives are &mdash; including the free-threaded build that ships alongside CPython 3.14."
    ],
    "sections": [
      {
        "title": "What the GIL actually is",
        "body": [
          {
            "type": "p",
            "html": "The GIL is one mutex per interpreter. A thread must hold it to execute Python bytecode or touch Python objects. Every other thread that wants to run Python code waits for it. Threads are real OS threads &mdash; the kernel schedules them freely &mdash; but only the one holding the GIL makes progress in Python code."
          },
          {
            "type": "code",
            "src": "import sys, threading\n\nprint(\"GIL enabled:\", sys._is_gil_enabled())\nprint(\"switch interval:\", sys.getswitchinterval(), \"seconds\")\nprint(\"threads right now:\", threading.active_count())",
            "label": null,
            "output": "GIL enabled: True\nswitch interval: 0.005 seconds\nthreads right now: 1",
            "isError": false
          },
          {
            "type": "p",
            "html": "The switch interval is the heart of the scheduling policy. A thread waiting for the GIL waits for up to that long (5&nbsp;ms), then sets a &ldquo;drop request&rdquo; flag. The running thread checks that flag between bytecodes, releases the lock, and the OS decides who gets it next."
          },
          {
            "type": "p",
            "html": "Why a single lock? CPython manages memory with reference counts, and every <code>x = obj</code> or function call bumps a count. Making each of those increments atomic would slow down every single-threaded program. One coarse lock makes all of it safe for the price of one acquire per time slice, and it makes C extensions easy to write because they can assume nobody else is mutating Python objects underneath them."
          },
          {
            "type": "note",
            "text": "The GIL protects the <em>interpreter&rsquo;s</em> internal state &mdash; refcounts, allocator, object internals. It was never designed to protect <em>your</em> data."
          }
        ]
      },
      {
        "title": "When the GIL is released",
        "body": [
          {
            "type": "p",
            "html": "A thread gives up the GIL in three situations:"
          },
          {
            "type": "table",
            "head": [
              "Trigger",
              "Who does it",
              "Example"
            ],
            "rows": [
              [
                "Switch interval expires",
                "The interpreter, between bytecodes",
                "A pure-Python loop that runs for more than 5&nbsp;ms while another thread is waiting"
              ],
              [
                "Blocking system call",
                "The C code around the call",
                "<code>socket.recv</code>, <code>file.read</code>, <code>time.sleep</code>, <code>select</code>, <code>subprocess.wait</code>"
              ],
              [
                "Long C computation",
                "Extension authors, explicitly",
                "<code>hashlib</code> on large buffers, <code>zlib</code>, most of NumPy, image codecs"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The second row is why threads work well for I/O. While one thread is blocked in the kernel waiting for a socket, it does not hold the GIL, so every other thread keeps running Python code."
          },
          {
            "type": "code",
            "src": "import threading, time\n\ndef fake_io():\n    time.sleep(0.2)          # releases the GIL while blocked\n\nstart = time.perf_counter()\nfor _ in range(5):\n    fake_io()\nsequential = time.perf_counter() - start\n\nstart = time.perf_counter()\nthreads = [threading.Thread(target=fake_io) for _ in range(5)]\nfor t in threads: t.start()\nfor t in threads: t.join()\nthreaded = time.perf_counter() - start\n\nprint(f\"sequential ~ {sequential:.1f}s\")\nprint(f\"threaded   ~ {threaded:.1f}s\")",
            "label": "five 0.2 s waits, one after another vs. overlapped",
            "output": "sequential ~ 1.0s\nthreaded   ~ 0.2s",
            "isError": false
          },
          {
            "type": "p",
            "html": "Five waits overlap into one. The same is true for real network calls, disk reads and database queries: the time is spent in the kernel, not in bytecode."
          }
        ]
      },
      {
        "title": "Why CPU-bound threads do not speed up",
        "body": [
          {
            "type": "p",
            "html": "Now make the work pure computation. There is no blocking call, so the only way the GIL changes hands is the switch interval, and only one thread is ever doing useful work. Two threads doing half the work each take as long as one thread doing all of it &mdash; often a little longer, because they now fight over the lock."
          },
          {
            "type": "code",
            "src": "import threading, time\n\ndef count(n):\n    while n:\n        n -= 1\n\nN = 4_000_000\n\nstart = time.perf_counter()\ncount(N)\none = time.perf_counter() - start\n\nstart = time.perf_counter()\na = threading.Thread(target=count, args=(N // 2,))\nb = threading.Thread(target=count, args=(N // 2,))\na.start(); b.start(); a.join(); b.join()\ntwo = time.perf_counter() - start\n\nprint(\"two threads at least 70% as slow as one:\", two > one * 0.7)\nprint(\"two threads at least 1.8x faster:       \", two < one / 1.8)",
            "label": "half the work each, on a multi-core machine",
            "output": "two threads at least 70% as slow as one: True\ntwo threads at least 1.8x faster:        False",
            "isError": false
          },
          {
            "type": "p",
            "html": "On a machine with plenty of cores the threaded version still cannot get close to 2x, because the two threads take turns rather than running side by side."
          },
          {
            "type": "p",
            "html": "The way around it is to stop sharing one interpreter. <code>multiprocessing</code> and <code>ProcessPoolExecutor</code> start separate Python processes, each with its own GIL, so they genuinely run on separate cores. The price is that arguments and results are pickled across a pipe, and every process pays interpreter start-up."
          },
          {
            "type": "code",
            "src": "from concurrent.futures import ProcessPoolExecutor\n\ndef count(n):\n    total = 0\n    for i in range(n):\n        total += i * i\n    return total\n\nif __name__ == \"__main__\":          # required: workers re-import this file\n    with ProcessPoolExecutor(max_workers=4) as pool:\n        results = list(pool.map(count, [200_000] * 4))\n    print(results == [count(200_000)] * 4)\n    print(len(results), \"chunks computed in separate processes\")",
            "label": null,
            "output": "True\n4 chunks computed in separate processes",
            "isError": false
          },
          {
            "type": "note",
            "text": "Process pools pay off when each task does much more work than it costs to pickle its input and output. Sending a 50&nbsp;MB list to a worker so it can add one to each element is slower than doing it in the parent."
          }
        ]
      },
      {
        "title": "The GIL does not make your code thread-safe",
        "body": [
          {
            "type": "p",
            "html": "This is the misconception that causes real bugs. The GIL guarantees that one <em>bytecode</em> runs at a time. It says nothing about a <em>statement</em>. <code>counter += 1</code> is several bytecodes: load, add, store. A switch can land between the load and the store."
          },
          {
            "type": "code",
            "src": "import dis\n\ncounter = 0\ndef bump():\n    global counter\n    counter += 1\n\ndis.dis(bump)",
            "label": "one line of Python, several steps",
            "output": "  4           RESUME                   0\n\n  6           LOAD_GLOBAL              0 (counter)\n              LOAD_SMALL_INT           1\n              BINARY_OP               13 (+=)\n              STORE_GLOBAL             0 (counter)\n              LOAD_CONST               1 (None)\n              RETURN_VALUE",
            "isError": false
          },
          {
            "type": "p",
            "html": "The window is small, so a naive demo often happens to get lucky. Widen it with <code>time.sleep(0)</code> &mdash; which releases the GIL on purpose &mdash; and the lost updates show up every time:"
          },
          {
            "type": "code",
            "src": "import threading, time\n\ncounter = 0\n\ndef worker():\n    global counter\n    for _ in range(1000):\n        value = counter\n        time.sleep(0)            # another thread runs here\n        counter = value + 1\n\nthreads = [threading.Thread(target=worker) for _ in range(4)]\nfor t in threads: t.start()\nfor t in threads: t.join()\n\nprint(\"expected 4000, got 4000:\", counter == 4000)\nprint(\"updates were lost:\", counter < 4000)",
            "label": "read, yield, write",
            "output": "expected 4000, got 4000: False\nupdates were lost: True",
            "isError": false
          },
          {
            "type": "code",
            "src": "import threading, time\n\ncounter = 0\nlock = threading.Lock()\n\ndef worker():\n    global counter\n    for _ in range(1000):\n        with lock:               # read-modify-write is now one unit\n            value = counter\n            time.sleep(0)\n            counter = value + 1\n\nthreads = [threading.Thread(target=worker) for _ in range(4)]\nfor t in threads: t.start()\nfor t in threads: t.join()\nprint(counter)",
            "label": "the fix",
            "output": "4000",
            "isError": false
          },
          {
            "type": "p",
            "html": "Single operations on built-in containers &mdash; <code>list.append</code>, <code>dict[key] = value</code>, <code>deque.popleft</code> &mdash; happen inside one C call and are atomic in practice. Anything that reads, decides, then writes (<code>d[k] += 1</code>, <code>if k not in d: d[k] = ...</code>) is not."
          },
          {
            "type": "caveat",
            "text": "The atomicity of single built-in operations is a CPython behaviour, not a language guarantee. The free-threaded build keeps it by giving containers per-object locks, but code that relies on it is relying on the implementation. <code>queue.Queue</code> and <code>threading.Lock</code> are the documented tools."
          }
        ]
      },
      {
        "title": "Threads, processes, asyncio &mdash; which one",
        "body": [
          {
            "type": "p",
            "html": "The right tool depends on where the time goes, not on how much work there is."
          },
          {
            "type": "table",
            "head": [
              "Workload",
              "Use",
              "Why not the others"
            ],
            "rows": [
              [
                "Many slow network calls, blocking library (<code>requests</code>, DB driver)",
                "<code>ThreadPoolExecutor</code>",
                "Processes waste memory waiting; asyncio needs an async library"
              ],
              [
                "Thousands of concurrent connections, async library available",
                "<code>asyncio</code>",
                "Thousands of OS threads cost memory and context switches"
              ],
              [
                "Pure-Python number crunching",
                "<code>ProcessPoolExecutor</code> (or free-threaded build)",
                "Threads serialize on the GIL; asyncio is one thread"
              ],
              [
                "NumPy / hashing / compression on big buffers",
                "Threads are fine",
                "The C code releases the GIL, so threads really do run in parallel"
              ],
              [
                "Mixed: async server that must do some CPU work",
                "asyncio + <code>run_in_executor</code> with a process pool",
                "Doing CPU work on the event loop stalls every connection"
              ]
            ]
          }
        ]
      },
      {
        "title": "Getting rid of it: free-threading and subinterpreters",
        "body": [
          {
            "type": "p",
            "html": "Two efforts attack the problem from different sides."
          },
          {
            "type": "p",
            "html": "<strong>Free-threaded CPython</strong> (PEP 703) is a separate build &mdash; installed as <code>python3.14t</code> &mdash; with no GIL at all. It was experimental in 3.13 and is officially supported from 3.14 (PEP 779). Making it work took biased reference counting (cheap non-atomic increments for the owning thread), immortal objects, the <code>mimalloc</code> allocator and per-object locks on containers. Single-threaded code pays a few percent for all of that; C extensions must be rebuilt and declare they are safe, otherwise the interpreter turns the GIL back on."
          },
          {
            "type": "p",
            "html": "<strong>Subinterpreters</strong> keep the GIL but give each interpreter its own (PEP 684, 3.12). From 3.14 they are exposed as <code>concurrent.interpreters</code> and <code>InterpreterPoolExecutor</code>: isolated like processes, but inside one process and cheaper to start."
          },
          {
            "type": "code",
            "src": "import sys, sysconfig\nfrom concurrent.futures import InterpreterPoolExecutor\n\ndef square(n):\n    return n * n\n\nprint(\"free-threaded build:\", bool(sysconfig.get_config_var(\"Py_GIL_DISABLED\")))\nprint(\"GIL currently enabled:\", sys._is_gil_enabled())\n\nif __name__ == \"__main__\":\n    with InterpreterPoolExecutor(max_workers=2) as pool:\n        print(list(pool.map(square, range(6))))",
            "label": "checking the build, and a pool of isolated interpreters",
            "output": "free-threaded build: False\nGIL currently enabled: True\n[0, 1, 4, 9, 16, 25]",
            "isError": false
          },
          {
            "type": "note",
            "text": "On a default CPython build, CPU parallelism means processes (or interpreters). Only reach for the free-threaded build when every C extension you import supports it."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "If Python has a GIL, why do I still need locks?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Because the GIL makes each <em>bytecode</em> atomic, not each statement or each piece of your logic. A read-modify-write such as <code>balance -= amount</code> is a load, a subtract and a store; a thread switch between the load and the store loses the other thread&rsquo;s update. Check-then-act sequences are worse:"
          },
          {
            "type": "code",
            "src": "import threading, time\n\nstock = {\"widget\": 1}\nsold = []\n\ndef buy(who):\n    if stock[\"widget\"] > 0:      # both threads see 1 ...\n        time.sleep(0.01)         # ... pretend to charge the card\n        stock[\"widget\"] -= 1\n        sold.append(who)\n\nts = [threading.Thread(target=buy, args=(n,)) for n in (\"ann\", \"bob\")]\nfor t in ts: t.start()\nfor t in ts: t.join()\nprint(sold, stock)",
            "label": null,
            "output": "['ann', 'bob'] {'widget': -1}",
            "isError": false
          },
          {
            "type": "p",
            "html": "Both buyers got the last widget and the stock went negative. Wrapping the check and the decrement in one <code>with lock:</code> fixes it. The GIL also disappears entirely on the free-threaded build, so code that &ldquo;worked because of the GIL&rdquo; breaks there."
          }
        ]
      },
      {
        "q": "You need to download 10,000 URLs and then resize 10,000 images. Which concurrency model do you use for each?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Downloading is I/O-bound: nearly all the time is spent waiting on the network with the GIL released. Use <code>asyncio</code> with an async HTTP client and a semaphore to cap concurrency, or a <code>ThreadPoolExecutor</code> of a few dozen threads if the client library is blocking. Processes would work but waste memory on idle interpreters."
          },
          {
            "type": "p",
            "html": "Resizing is CPU-bound. If the resize happens in a C library that releases the GIL (Pillow does for most operations), threads can already use several cores. If it is pure Python, use a <code>ProcessPoolExecutor</code> sized to the core count and pass <em>file paths</em> to workers, not image bytes, so the pickling cost stays small."
          },
          {
            "type": "p",
            "html": "The follow-up interviewers like: in a pipeline doing both, run the downloads on the event loop and hand each finished file to a process pool via <code>loop.run_in_executor</code>, so neither stage blocks the other."
          }
        ]
      },
      {
        "q": "Why hasn&rsquo;t the GIL simply been removed?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "It has been tried many times. Greg Stein&rsquo;s 1999 patch replaced it with fine-grained locks and made single-threaded code roughly twice as slow; Larry Hastings&rsquo; Gilectomy hit the same wall. The costs are:"
          },
          {
            "type": "p",
            "html": "<strong>Reference counting</strong> &mdash; every incref/decref would have to be an atomic instruction, which is far slower than a plain increment and hammers shared cache lines.<br><strong>C API compatibility</strong> &mdash; thousands of extensions assume the GIL protects them.<br><strong>Single-thread speed</strong> &mdash; the core team&rsquo;s stated rule was that removing the GIL must not make ordinary programs meaningfully slower."
          },
          {
            "type": "p",
            "html": "PEP 703 got past these with <em>biased reference counting</em> (the owning thread uses non-atomic ops; others use atomic ones on a separate field), <em>immortal objects</em> whose counts never change (<code>None</code>, small ints), deferred refcounting for functions and modules, <code>mimalloc</code> for thread-safe allocation, and per-object critical sections for <code>list</code>/<code>dict</code>. It ships as a separate build so extensions can opt in gradually."
          }
        ]
      },
      {
        "q": "What is the switch interval, and what is the &ldquo;convoy effect&rdquo;?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Since Python 3.2 a waiting thread waits up to <code>sys.getswitchinterval()</code> (5&nbsp;ms by default) and then sets a flag asking the holder to drop the GIL. The holder checks the flag at safe points between bytecodes. The old scheme counted 100 &ldquo;ticks&rdquo; instead, which behaved terribly on multi-core machines."
          },
          {
            "type": "p",
            "html": "The convoy effect: an I/O thread that does a short read releases the GIL, gets its data almost instantly, and then has to wait up to a full interval behind a CPU-bound thread before it can process that data &mdash; for every single read. A thread doing thousands of small reads runs orders of magnitude slower than it would alone. Lowering the switch interval helps latency at the cost of more switching overhead:"
          },
          {
            "type": "code",
            "src": "import sys\nprint(sys.getswitchinterval())\nsys.setswitchinterval(0.001)\nprint(sys.getswitchinterval())",
            "label": null,
            "output": "0.005\n0.001",
            "isError": false
          }
        ]
      },
      {
        "q": "Is <code>d[key] += 1</code> thread-safe? What about <code>list.append</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>list.append(x)</code> is one C function call on a built-in type, and CPython will not switch threads in the middle of it, so in practice it is atomic. <code>d[key] += 1</code> is a lookup, an add and a store &mdash; three steps with switch points between them, so it is not."
          },
          {
            "type": "code",
            "src": "import dis\ndef inc(d, key):\n    d[key] += 1\ndis.dis(inc)",
            "label": null,
            "output": "  2           RESUME                   0\n\n  3           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (d, key)\n              COPY                     2\n              COPY                     2\n              BINARY_OP               26 ([])\n              LOAD_SMALL_INT           1\n              BINARY_OP               13 (+=)\n              SWAP                     3\n              SWAP                     2\n              STORE_SUBSCR\n              LOAD_CONST               1 (None)\n              RETURN_VALUE",
            "isError": false
          },
          {
            "type": "p",
            "html": "Use <code>collections.Counter</code> updates under a lock, <code>queue.Queue</code> for hand-offs, or give each thread its own counter and merge at the end. The last option is usually fastest because it needs no locking at all."
          }
        ]
      },
      {
        "q": "Why does <code>multiprocessing</code> code need <code>if __name__ == &quot;__main__&quot;</code>?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "With the <em>spawn</em> start method a worker is a brand-new interpreter. To find the function you asked it to run, it imports your main module. Without the guard, that import runs the top-level code again &mdash; which starts another pool, which spawns more workers, which import the module&hellip; CPython detects this and raises a <code>RuntimeError</code> telling you to add the guard."
          },
          {
            "type": "code",
            "src": "import multiprocessing as mp\nprint(mp.get_start_method())",
            "label": "the default on this build machine",
            "output": "spawn",
            "isError": false
          },
          {
            "type": "p",
            "html": "<em>spawn</em> is the default on macOS and Windows. Linux used <em>fork</em> for years, which copies the parent&rsquo;s memory and so did not need the guard &mdash; but forking a process that has threads can deadlock, so 3.14 made <em>forkserver</em> the Linux default. Code without the guard that has only ever been run on Linux is now more likely to break."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: thread state and the GIL",
        "url": "https://docs.python.org/3/c-api/init.html#thread-state-and-the-global-interpreter-lock"
      },
      {
        "label": "PEP 703 — Making the GIL optional",
        "url": "https://peps.python.org/pep-0703/"
      },
      {
        "label": "PEP 734 — Multiple interpreters in the stdlib",
        "url": "https://peps.python.org/pep-0734/"
      },
      {
        "label": "Python docs: free-threading HOWTO",
        "url": "https://docs.python.org/3/howto/free-threading-python.html"
      }
    ]
  },
  {
    "id": "memory",
    "title": "Memory Management",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "Python frees you from <code>malloc</code> and <code>free</code>, but not from memory. CPython uses two mechanisms together: <strong>reference counting</strong>, which frees almost everything the instant it becomes unreachable, and a <strong>cycle collector</strong>, which cleans up the objects reference counting cannot. Underneath both sits a specialised allocator for small objects.",
      "Knowing how these fit together explains why <code>__del__</code> runs when it does, why a program can hold on to memory after you delete a huge list, why <code>lru_cache</code> on a method leaks, and what <code>__slots__</code> actually saves."
    ],
    "sections": [
      {
        "title": "Names are references, objects carry a count",
        "body": [
          {
            "type": "p",
            "html": "A variable is a name bound to an object. Assignment never copies; it adds another reference. Every object stores how many references point at it, and <code>sys.getrefcount</code> reports that number &mdash; plus whatever temporary reference the call itself creates."
          },
          {
            "type": "code",
            "src": "import sys\n\ndata = [1, 2, 3]\nprint(sys.getrefcount(data))\n\nalias = data\nbox = [data, data]\nprint(sys.getrefcount(data))\n\ndel alias\nbox.clear()\nprint(sys.getrefcount(data))",
            "label": null,
            "output": "2\n5\n2",
            "isError": false
          },
          {
            "type": "p",
            "html": "Each name, container slot, attribute and stack frame that refers to an object counts. <code>del</code> removes a <em>name</em> and decrements the count; it does not destroy the object unless that was the last reference."
          },
          {
            "type": "caveat",
            "text": "The absolute numbers depend on the interpreter version &mdash; newer CPythons avoid some temporary references altogether. Compare counts before and after an operation rather than reading meaning into the raw value."
          }
        ]
      },
      {
        "title": "Deterministic destruction",
        "body": [
          {
            "type": "p",
            "html": "When a count hits zero, CPython deallocates the object immediately &mdash; inside the operation that dropped the last reference. That is why this prints in exactly this order:"
          },
          {
            "type": "code",
            "src": "class Resource:\n    def __init__(self, name):\n        self.name = name\n        print(\"open \", name)\n    def __del__(self):\n        print(\"close\", self.name)\n\ndef work():\n    r = Resource(\"temp\")\n    print(\"working\")\n# r goes out of scope when work() returns\n\nwork()\nprint(\"after work()\")\n\na = Resource(\"a\")\na = Resource(\"b\")        # rebinding drops the last reference to \"a\"\nprint(\"end of script\")",
            "label": null,
            "output": "open  temp\nworking\nclose temp\nafter work()\nopen  a\nopen  b\nclose a\nend of script\nclose b",
            "isError": false
          },
          {
            "type": "p",
            "html": "Many Python programs quietly rely on this &mdash; files closing when the variable goes away, for instance. Do not. PyPy, GraalPy and the free-threaded build&rsquo;s deferred reference counting do not all free at the same moment, and an object caught in a reference cycle is not freed by counting at all. Use <code>with</code> for anything that must be released at a known point."
          }
        ]
      },
      {
        "title": "Reference cycles and the garbage collector",
        "body": [
          {
            "type": "p",
            "html": "Reference counting has one blind spot: objects that refer to each other. When the outside world lets go, each member of the cycle still has a count of at least one, so nothing is freed."
          },
          {
            "type": "code",
            "src": "import gc, weakref\n\nclass Node:\n    pass\n\ngc.collect()                   # start from a clean slate\ngc.disable()                   # so the collector cannot step in early\n\na, b = Node(), Node()\na.other, b.other = b, a        # a <-> b\nprobe = weakref.ref(a)         # watches a without keeping it alive\n\ndel a, b\nprint(\"alive after del:       \", probe() is not None)\n\nfound = gc.collect()\nprint(\"alive after gc.collect:\", probe() is not None)\nprint(\"unreachable objects found:\", found)",
            "label": null,
            "output": "alive after del:        True\nalive after gc.collect: False\nunreachable objects found: 2",
            "isError": false
          },
          {
            "type": "p",
            "html": "The cycle collector finds garbage by elimination. For every container object it tracks (lists, dicts, class instances &mdash; not ints or strings), it subtracts the references that come from <em>other tracked objects</em>. Whatever still has a positive count is referenced from outside and is alive, along with everything reachable from it. The rest is an isolated cycle, and it is freed."
          },
          {
            "type": "p",
            "html": "Since Python 3.4 (PEP 442), cycles containing objects with <code>__del__</code> are collected too; before that they were parked in <code>gc.garbage</code> forever."
          }
        ]
      },
      {
        "title": "Generations, thresholds and incremental collection",
        "body": [
          {
            "type": "p",
            "html": "Scanning every object on every allocation would be ruinous, so the collector uses the <em>generational hypothesis</em>: most objects die young. New containers start in the young generation, which is scanned often; survivors get promoted and scanned rarely."
          },
          {
            "type": "code",
            "src": "import gc\nprint(\"thresholds:\", gc.get_threshold())\nprint(\"tracked int:\", gc.is_tracked(42))\nprint(\"tracked str:\", gc.is_tracked(\"hello\"))\nprint(\"tracked []: \", gc.is_tracked([]))\nprint(\"tracked obj:\", gc.is_tracked(object.__new__(type(\"T\", (), {}))))",
            "label": null,
            "output": "thresholds: (2000, 10, 10)\ntracked int: False\ntracked str: False\ntracked []:  True\ntracked obj: True",
            "isError": false
          },
          {
            "type": "p",
            "html": "Atomic objects like ints and strings cannot hold references to other objects, so they can never be part of a cycle and the collector never looks at them. Only containers are tracked."
          },
          {
            "type": "p",
            "html": "The first threshold is how many net container allocations trigger a young collection. Python 3.14 replaced the classic three-generation collector with an <em>incremental</em> one: a young generation plus an old generation that is scanned a slice at a time, so a program with millions of long-lived objects no longer suffers one huge full-collection pause."
          },
          {
            "type": "table",
            "head": [
              "Tool",
              "What it does",
              "When to use it"
            ],
            "rows": [
              [
                "<code>gc.collect()</code>",
                "Run a full collection now, return objects found",
                "Tests, and after tearing down a big object graph"
              ],
              [
                "<code>gc.disable()</code>",
                "Stop automatic cycle collection (refcounting still works)",
                "Short batch jobs that create no cycles; latency-critical sections"
              ],
              [
                "<code>gc.freeze()</code>",
                "Move all current objects to a permanent generation that is never scanned",
                "Pre-fork servers: stops the GC touching pages the children share"
              ],
              [
                "<code>gc.set_threshold()</code>",
                "Collect less often",
                "Allocation-heavy programs where GC time shows up in profiles"
              ]
            ]
          }
        ]
      },
      {
        "title": "How objects are allocated: pymalloc",
        "body": [
          {
            "type": "p",
            "html": "Python allocates huge numbers of small, short-lived objects. Calling the system <code>malloc</code> for each would be slow, so CPython routes every request of 512 bytes or less through <strong>pymalloc</strong>:"
          },
          {
            "type": "table",
            "head": [
              "Layer",
              "Size",
              "Holds"
            ],
            "rows": [
              [
                "Arena",
                "1 MiB, from the OS via <code>mmap</code>",
                "Many pools"
              ],
              [
                "Pool",
                "16 KiB",
                "Blocks of one size class only"
              ],
              [
                "Block",
                "A multiple of 16 bytes, up to 512",
                "One object"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Freed blocks go back on their pool&rsquo;s free list and are reused immediately by the next object of that size, which is very fast. Larger requests go straight to the system allocator."
          },
          {
            "type": "p",
            "html": "The catch: an arena is returned to the operating system only when <em>every</em> block in it is free. Build a million small objects, delete all but one in each arena, and the process keeps nearly all that memory. That is fragmentation, and it is why resident memory often does not drop after a big <code>del</code>."
          },
          {
            "type": "p",
            "html": "Containers also over-allocate so that appends are cheap on average. Watch a list&rsquo;s size step up only occasionally:"
          },
          {
            "type": "code",
            "src": "import sys\n\nitems, last = [], None\nfor i in range(20):\n    size = sys.getsizeof(items)\n    if size != last:\n        print(f\"len={len(items):2}  bytes={size}\")\n        last = size\n    items.append(i)",
            "label": null,
            "output": "len= 0  bytes=56\nlen= 1  bytes=88\nlen= 5  bytes=120\nlen= 9  bytes=184\nlen=17  bytes=248",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>sys.getsizeof</code> is <em>shallow</em>: it counts the list&rsquo;s pointer array, not the objects the pointers lead to. A list of a thousand 1&nbsp;KB strings is reported as about 8&nbsp;KB."
          }
        ]
      },
      {
        "title": "Sharing, caching and immortal objects",
        "body": [
          {
            "type": "p",
            "html": "CPython avoids creating objects it can share. Integers from -5 to 256 are pre-built singletons, and short identifier-like strings are <em>interned</em> so equal ones are the same object."
          },
          {
            "type": "code",
            "src": "import sys\n\na, b = int(\"256\"), int(\"256\")\nc, d = int(\"257\"), int(\"257\")\nprint(\"256 is 256:\", a is b)\nprint(\"257 is 257:\", c is d)\n\ns1 = \"\".join([\"hello\", \"_\", \"world\"])\ns2 = \"hello_world\"\nprint(\"equal:\", s1 == s2, \" same object:\", s1 is s2)\nprint(\"after intern:\", sys.intern(s1) is s2)",
            "label": null,
            "output": "256 is 256: True\n257 is 257: False\nequal: True  same object: False\nafter intern: True",
            "isError": false
          },
          {
            "type": "p",
            "html": "Since 3.12 (PEP 683) objects like <code>None</code>, <code>True</code> and the small ints are <strong>immortal</strong>: their reference count is pinned to a huge sentinel and increments are skipped. That avoids writing to them from every thread and every forked child, which matters for both the free-threaded build and copy-on-write memory sharing."
          },
          {
            "type": "code",
            "src": "import sys\nprint(sys.getrefcount(None))\nprint(sys.getrefcount(7))\nprint(sys._is_immortal(None), sys._is_immortal([]))",
            "label": null,
            "output": "3221225472\n3221225472\nTrue False",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "The small-int range, string interning and immortality are CPython implementation details. Never use <code>is</code> to compare numbers or strings in real code."
          }
        ]
      },
      {
        "title": "Measuring and cutting memory: __slots__ and tracemalloc",
        "body": [
          {
            "type": "p",
            "html": "By default every instance carries a <code>__dict__</code> so you can add attributes at any time. When you create millions of small objects, that dict is most of the cost. <code>__slots__</code> replaces it with fixed storage."
          },
          {
            "type": "code",
            "src": "import tracemalloc\n\nclass Plain:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n\nclass Slotted:\n    __slots__ = (\"x\", \"y\")\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n\ndef measure(cls):\n    tracemalloc.start()\n    objs = [cls(i, i) for i in range(50_000)]\n    size, _ = tracemalloc.get_traced_memory()\n    tracemalloc.stop()\n    return size\n\nplain, slotted = measure(Plain), measure(Slotted)\nprint(\"slots use less memory:\", slotted < plain)\nprint(\"saving is over 30%:\", slotted < plain * 0.7)\n\ns = Slotted(1, 2)\ntry:\n    s.z = 3\nexcept AttributeError as e:\n    print(\"AttributeError:\", e)",
            "label": null,
            "output": "slots use less memory: True\nsaving is over 30%: True\nAttributeError: 'Slotted' object has no attribute 'z' and no __dict__ for setting new attributes",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>tracemalloc</code> records the Python stack for every allocation, so it can tell you <em>which line</em> is holding memory. Taking two snapshots and diffing them is the standard way to find a leak:"
          },
          {
            "type": "code",
            "src": "import tracemalloc\n\ncache = []\ndef leaky(n):\n    cache.append(bytearray(1000))   # a new 1 KB buffer every call\n\ntracemalloc.start()\nbefore = tracemalloc.take_snapshot()\nfor i in range(2000):\n    leaky(i)\nafter = tracemalloc.take_snapshot()\n\ntop = after.compare_to(before, \"lineno\")[0]\nframe = top.traceback[0]\nprint(\"biggest growth at line\", frame.lineno)\nprint(f\"grew by about {top.size_diff / 1e6:.1f} MB\")",
            "label": null,
            "output": "biggest growth at line 5\ngrew by about 2.1 MB",
            "isError": false
          },
          {
            "type": "note",
            "text": "Reach for <code>__slots__</code> when you have many instances of a class with a fixed set of attributes. It also blocks typos like <code>self.nmae = ...</code>, but you lose <code>__dict__</code>, and weak references unless you add <code>__weakref__</code> to the slots."
          }
        ]
      },
      {
        "title": "Weak references",
        "body": [
          {
            "type": "p",
            "html": "A weak reference points at an object without adding to its count. When the last strong reference goes, the object is freed and the weak reference returns <code>None</code>. This is the tool for caches and observer lists that should not keep things alive."
          },
          {
            "type": "code",
            "src": "import weakref\n\nclass Image:\n    def __init__(self, name):\n        self.name = name\n\ncache = weakref.WeakValueDictionary()\n\nimg = Image(\"logo.png\")\ncache[\"logo\"] = img\nprint(\"cached:\", \"logo\" in cache)\n\ndel img                          # last strong reference gone\nprint(\"cached after del:\", \"logo\" in cache)",
            "label": null,
            "output": "cached: True\ncached after del: False",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Tool",
              "Holds keys",
              "Holds values",
              "Typical use"
            ],
            "rows": [
              [
                "<code>weakref.ref</code>",
                "&mdash;",
                "weakly",
                "Back-pointer from child to parent"
              ],
              [
                "<code>WeakValueDictionary</code>",
                "strongly",
                "weakly",
                "Cache of objects owned elsewhere"
              ],
              [
                "<code>WeakKeyDictionary</code>",
                "weakly",
                "strongly",
                "Attaching extra data to objects you do not own"
              ],
              [
                "<code>weakref.finalize</code>",
                "&mdash;",
                "&mdash;",
                "Reliable cleanup callback; safer than <code>__del__</code>"
              ]
            ]
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What is the difference between <code>del x</code> and freeing the object?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>del x</code> unbinds the name <code>x</code> and decrements the object&rsquo;s reference count. The object is freed only if that was the last reference. If a list, a closure, a global or a cycle still refers to it, it lives on."
          },
          {
            "type": "code",
            "src": "class Big:\n    def __del__(self):\n        print(\"freed\")\n\nb = Big()\nkeep = [b]\ndel b\nprint(\"after del b\")\nkeep.clear()\nprint(\"after clear\")",
            "label": null,
            "output": "after del b\nfreed\nafter clear",
            "isError": false
          }
        ]
      },
      {
        "q": "Why does <code>functools.lru_cache</code> on a method leak memory?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The cache lives on the <em>function</em>, which lives on the class, which lives for the whole program. <code>self</code> is part of every cache key, so the cache holds a strong reference to every instance that ever called the method. Those instances are never freed."
          },
          {
            "type": "code",
            "src": "import functools, gc, weakref\n\nclass Report:\n    @functools.lru_cache(maxsize=None)\n    def total(self):\n        return 42\n\nr = Report()\nr.total()\nprobe = weakref.ref(r)\ndel r\ngc.collect()\nprint(\"instance still alive:\", probe() is not None)\nprint(Report.total.cache_info())",
            "label": "the leak",
            "output": "instance still alive: True\nCacheInfo(hits=0, misses=1, maxsize=None, currsize=1)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Fixes: use <code>functools.cached_property</code> (stores the result on the instance, so it dies with it), keep the cache per instance in <code>__init__</code>, or move the cached computation to a module-level function whose arguments are plain values rather than <code>self</code>."
          },
          {
            "type": "code",
            "src": "import functools, gc, weakref\n\nclass Report:\n    @functools.cached_property\n    def total(self):\n        return 42\n\nr = Report()\nr.total\nprobe = weakref.ref(r)\ndel r\ngc.collect()\nprint(\"instance still alive:\", probe() is not None)",
            "label": "the fix",
            "output": "instance still alive: False",
            "isError": false
          }
        ]
      },
      {
        "q": "You delete a list of ten million objects but the process&rsquo;s memory barely drops. Why?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Several reasons, usually together:"
          },
          {
            "type": "p",
            "html": "<strong>Fragmentation in pymalloc</strong> &mdash; an arena goes back to the OS only when every block in it is free. A few survivors scattered across arenas pin them all.<br><strong>Free lists and caches</strong> &mdash; CPython keeps freed floats, tuples, frames and so on for reuse.<br><strong>The system allocator</strong> &mdash; large blocks freed with <code>free()</code> are often retained by libc for the next <code>malloc</code>.<br><strong>Something still references it</strong> &mdash; check with <code>gc.get_referrers</code> or a <code>weakref</code> probe."
          },
          {
            "type": "p",
            "html": "The memory is not lost &mdash; the next allocations reuse it. If peak memory is the problem, avoid materialising it: stream with generators, use <code>array</code> or NumPy for numbers (one buffer instead of millions of objects), or do the heavy work in a child process that exits and hands back only the result."
          }
        ]
      },
      {
        "q": "How would you find a memory leak in a long-running Python service?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Confirm it first: plot RSS over time under steady load. A leak climbs forever; fragmentation plateaus. Then:"
          },
          {
            "type": "p",
            "html": "1. Take two <code>tracemalloc</code> snapshots some minutes apart and <code>compare_to</code> by line &mdash; the top entries show which code is allocating memory that is not freed.<br>2. Count live objects by type (<code>gc.get_objects()</code>, or <code>objgraph.show_growth()</code>) to see what kind of object is piling up.<br>3. Follow <code>gc.get_referrers</code> back from one of those objects to see who is holding it."
          },
          {
            "type": "p",
            "html": "The usual suspects are unbounded module-level caches and dicts, <code>lru_cache(maxsize=None)</code> on methods, listeners registered and never removed, exceptions stored with their tracebacks (which hold every frame and its locals), and threads that never exit."
          }
        ]
      },
      {
        "q": "What does <code>sys.getsizeof</code> not tell you?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It reports the size of the object itself &mdash; not what it refers to. A container&rsquo;s size is its header plus its pointer array."
          },
          {
            "type": "code",
            "src": "import sys\n\nsmall = [\"a\" for _ in range(1000)]\nlarge = [\"a\" * 10_000 for _ in range(1000)]\nprint(sys.getsizeof(small) == sys.getsizeof(large))\n\ndef deep_size(obj, seen=None):\n    seen = set() if seen is None else seen\n    if id(obj) in seen:\n        return 0\n    seen.add(id(obj))\n    size = sys.getsizeof(obj)\n    if isinstance(obj, (list, tuple, set)):\n        size += sum(deep_size(x, seen) for x in obj)\n    elif isinstance(obj, dict):\n        size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())\n    return size\n\nprint(deep_size(large) > 100 * deep_size(small))",
            "label": null,
            "output": "True\nTrue",
            "isError": false
          },
          {
            "type": "p",
            "html": "The <code>seen</code> set matters: without it, shared objects are counted many times and cycles recurse forever."
          }
        ]
      },
      {
        "q": "What are immortal objects, and why did CPython add them?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "PEP 683 (3.12) marks some objects &mdash; <code>None</code>, <code>True</code>, <code>False</code>, small ints, interned strings created at start-up &mdash; with a special reference count that is never incremented or decremented. They are never freed."
          },
          {
            "type": "p",
            "html": "Two problems went away. Every <code>return None</code> used to write to <code>None</code>&rsquo;s refcount; after a <code>fork</code>, that write copied the memory page into every child, defeating copy-on-write sharing (Instagram&rsquo;s servers were the motivating case). And in the free-threaded build, thousands of threads writing to the same hot counters would contend on one cache line. Immortal objects are read-only in practice, so both costs vanish."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: gc — Garbage Collector interface",
        "url": "https://docs.python.org/3/library/gc.html"
      },
      {
        "label": "Python docs: tracemalloc",
        "url": "https://docs.python.org/3/library/tracemalloc.html"
      },
      {
        "label": "CPython internals: garbage collector design",
        "url": "https://github.com/python/cpython/blob/main/InternalDocs/garbage_collector.md"
      },
      {
        "label": "PEP 683 — Immortal objects",
        "url": "https://peps.python.org/pep-0683/"
      }
    ]
  },
  {
    "id": "bytecode",
    "title": "CPython Bytecode",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "Python is compiled. Not to machine code, but to <strong>bytecode</strong>: a compact instruction set for a stack-based virtual machine. Every function you write becomes a code object holding those instructions, and a big loop in C &mdash; the evaluation loop &mdash; executes them one at a time.",
      "Reading bytecode answers questions that are otherwise folklore: why locals are faster than globals, why <code>UnboundLocalError</code> exists, what <code>a, b = b, a</code> really does, and what the 3.11+ &ldquo;faster CPython&rdquo; work actually changed."
    ],
    "sections": [
      {
        "title": "From source to bytecode",
        "body": [
          {
            "type": "p",
            "html": "Running a module goes through a fixed pipeline:"
          },
          {
            "type": "table",
            "head": [
              "Stage",
              "Produces",
              "You can inspect it with"
            ],
            "rows": [
              [
                "Tokenizer",
                "A stream of tokens",
                "<code>tokenize</code>"
              ],
              [
                "Parser",
                "An abstract syntax tree",
                "<code>ast.parse</code>, <code>ast.dump</code>"
              ],
              [
                "Symbol table",
                "Which names are local, global, free or cell",
                "<code>symtable</code>"
              ],
              [
                "Compiler",
                "A code object: bytecode + constants + names",
                "<code>compile</code>, <code>dis</code>"
              ],
              [
                "Evaluation loop",
                "The running program",
                "<code>sys.settrace</code>, profilers"
              ]
            ]
          },
          {
            "type": "code",
            "src": "import ast\n\ntree = ast.parse(\"total = price * 2\")\nprint(ast.dump(tree.body[0], indent=2))",
            "label": "the AST for one statement",
            "output": "Assign(\n  targets=[\n    Name(id='total', ctx=Store())],\n  value=BinOp(\n    left=Name(id='price', ctx=Load()),\n    op=Mult(),\n    right=Constant(value=2)))",
            "isError": false
          },
          {
            "type": "code",
            "src": "co = compile(\"total = price * 2\", \"<demo>\", \"exec\")\nprint(type(co).__name__)\nprint(\"names: \", co.co_names)\nprint(\"consts:\", co.co_consts)\n\nimport dis\ndis.dis(co)",
            "label": "the same statement, compiled",
            "output": "code\nnames:  ('price', 'total')\nconsts: (2, None)\n  0           RESUME                   0\n\n  1           LOAD_NAME                0 (price)\n              LOAD_SMALL_INT           2\n              BINARY_OP                5 (*)\n              STORE_NAME               1 (total)\n              LOAD_CONST               1 (None)\n              RETURN_VALUE",
            "isError": false
          },
          {
            "type": "p",
            "html": "The code object keeps the bytecode separate from the data it refers to. Instructions carry small integer arguments that index into <code>co_names</code> (global and attribute names), <code>co_consts</code> (literals) or the local variable array."
          }
        ]
      },
      {
        "title": "Reading dis output",
        "body": [
          {
            "type": "p",
            "html": "The virtual machine is a <em>stack machine</em>: instructions push values onto an evaluation stack and pop them off. Each <code>dis</code> line is an instruction, its argument, and in brackets what that argument means."
          },
          {
            "type": "code",
            "src": "import dis\n\ndef area(width, height):\n    scale = 2\n    return width * height * scale\n\ndis.dis(area)",
            "label": null,
            "output": "  3           RESUME                   0\n\n  4           LOAD_SMALL_INT           2\n              STORE_FAST               2 (scale)\n\n  5           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (width, height)\n              BINARY_OP                5 (*)\n              LOAD_FAST_BORROW         2 (scale)\n              BINARY_OP                5 (*)\n              RETURN_VALUE",
            "isError": false
          },
          {
            "type": "p",
            "html": "Read it top to bottom: push <code>width</code> and <code>height</code>, multiply them (pop two, push one), push <code>scale</code>, multiply again, return the top of the stack. The numbers on the left are source line numbers. <code>RESUME</code> is a hook the interpreter uses for tracing and for checking whether it should switch threads."
          },
          {
            "type": "caveat",
            "text": "Bytecode is not a stable interface. Instruction names and their arguments change in every minor release &mdash; 3.14 added <code>LOAD_SMALL_INT</code> and the <code>_BORROW</code> variants you see above. Use <code>dis</code> to understand, never to build tools that must survive an upgrade."
          }
        ]
      },
      {
        "title": "Code objects and functions",
        "body": [
          {
            "type": "p",
            "html": "A code object is immutable and has no idea which module it lives in. A <em>function</em> is a code object bundled with the things needed to run it: its globals, default values, and closure cells."
          },
          {
            "type": "code",
            "src": "def make_counter(start=0):\n    count = start\n    def step(by=1):\n        nonlocal count\n        count += by\n        return count\n    return step\n\nstep = make_counter(10)\nco = step.__code__\n\nprint(\"name:      \", co.co_name)\nprint(\"args:      \", co.co_argcount, co.co_varnames[:co.co_argcount])\nprint(\"free vars: \", co.co_freevars)\nprint(\"defaults:  \", step.__defaults__)\nprint(\"closure:   \", step.__closure__[0].cell_contents)\nprint(step(), step(5))\nprint(\"closure:   \", step.__closure__[0].cell_contents)",
            "label": null,
            "output": "name:       step\nargs:       1 ('by',)\nfree vars:  ('count',)\ndefaults:   (1,)\nclosure:    10\n11 16\nclosure:    16",
            "isError": false
          },
          {
            "type": "p",
            "html": "Many functions can share one code object: every call to <code>make_counter</code> creates a new <em>function</em> for <code>step</code>, but they all point at the same <code>__code__</code>, each with its own closure cell."
          }
        ]
      },
      {
        "title": "Locals are array slots, globals are dict lookups",
        "body": [
          {
            "type": "p",
            "html": "The compiler decides at compile time whether every name is local, global or a closure variable, and emits a different instruction for each."
          },
          {
            "type": "code",
            "src": "import dis\n\nLIMIT = 10\n\ndef check(value):\n    return value < LIMIT and len(str(value)) > 1\n\ndis.dis(check)",
            "label": null,
            "output": "  5           RESUME                   0\n\n  6           LOAD_FAST_BORROW         0 (value)\n              LOAD_GLOBAL              0 (LIMIT)\n              COMPARE_OP               2 (<)\n              COPY                     1\n              TO_BOOL\n              POP_JUMP_IF_FALSE       24 (to L1)\n              NOT_TAKEN\n              POP_TOP\n              LOAD_GLOBAL              3 (len + NULL)\n              LOAD_GLOBAL              5 (str + NULL)\n              LOAD_FAST_BORROW         0 (value)\n              CALL                     1\n              CALL                     1\n              LOAD_SMALL_INT           1\n              COMPARE_OP             132 (>)\n      L1:     RETURN_VALUE",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Instruction",
              "Where it looks",
              "Cost"
            ],
            "rows": [
              [
                "<code>LOAD_FAST</code>",
                "Slot <em>n</em> of the frame&rsquo;s local array",
                "An index"
              ],
              [
                "<code>LOAD_DEREF</code>",
                "A closure cell",
                "An index plus one pointer hop"
              ],
              [
                "<code>LOAD_GLOBAL</code>",
                "Module dict, then builtins dict",
                "Up to two hash lookups (cached by specialization)"
              ],
              [
                "<code>LOAD_ATTR</code>",
                "Instance dict, class MRO, descriptors",
                "Potentially many lookups (also specialized)"
              ]
            ]
          },
          {
            "type": "p",
            "html": "That is why the old trick of aliasing a global or a method to a local before a hot loop (<code>append = out.append</code>) used to help a lot. Since 3.11 the specializing interpreter caches most global and attribute lookups, so the gain is much smaller. Measure before doing it."
          },
          {
            "type": "p",
            "html": "Deciding scope at compile time has a visible consequence: if a function assigns to a name <em>anywhere</em>, that name is local for the <em>whole</em> function."
          },
          {
            "type": "code",
            "src": "x = 10\n\ndef show():\n    print(x)      # compiled as LOAD_FAST: x is local here ...\n    x = 5         # ... because of this line\n\nshow()",
            "label": null,
            "output": "Traceback (most recent call last):\n  File \"bytecode_s3_5.py\", line 7, in <module>\n    show()\n    ~~~~^^\n  File \"bytecode_s3_5.py\", line 4, in show\n    print(x)      # compiled as LOAD_FAST: x is local here ...\n          ^\nUnboundLocalError: cannot access local variable 'x' where it is not associated with a value",
            "isError": true
          }
        ]
      },
      {
        "title": "What the compiler optimises",
        "body": [
          {
            "type": "p",
            "html": "CPython&rsquo;s compiler is deliberately simple, but it does fold constants and pick better literal types when the result cannot change behaviour."
          },
          {
            "type": "code",
            "src": "def timeouts():\n    seconds = 24 * 60 * 60\n    banner = \"-\" * 10\n    return seconds, banner\n\ndef is_vowel(c):\n    return c in [\"a\", \"e\", \"i\", \"o\", \"u\"]\n\ndef is_digit(c):\n    return c in {\"0\", \"1\", \"2\"}\n\nprint(timeouts.__code__.co_consts)\nprint(is_vowel.__code__.co_consts)\nprint(is_digit.__code__.co_consts)",
            "label": null,
            "output": "(24, 86400, '----------')\n('a', ('a', 'e', 'i', 'o', 'u'))\n('0', frozenset({'2', '1', '0'}))",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>24 * 60 * 60</code> became <code>86400</code> at compile time. A list literal used only for <code>in</code> became a tuple (a list would have to be rebuilt on every call), and a set literal became a <code>frozenset</code> constant."
          },
          {
            "type": "p",
            "html": "Equal constants are also stored once per compilation &mdash; the whole module, including every function in it, shares them. That is the real reason behind a famous identity puzzle (see the interview questions below)."
          }
        ]
      },
      {
        "title": "Comprehensions, generators and flags",
        "body": [
          {
            "type": "p",
            "html": "The compiler marks special kinds of function with flags in <code>co_flags</code>. Calling a function whose code has the <code>GENERATOR</code> flag does not run the body at all &mdash; it creates a generator object that will run it on demand."
          },
          {
            "type": "code",
            "src": "import inspect\n\ndef plain():  return 1\ndef gen():    yield 1\nasync def coro(): return 1\n\nfor fn in (plain, gen, coro):\n    flags = inspect.CO_GENERATOR | inspect.CO_COROUTINE\n    kind = {inspect.CO_GENERATOR: \"generator\",\n            inspect.CO_COROUTINE: \"coroutine\"}.get(fn.__code__.co_flags & flags, \"plain\")\n    print(f\"{fn.__name__:6} -> {kind}\")",
            "label": null,
            "output": "plain  -> plain\ngen    -> generator\ncoro   -> coroutine",
            "isError": false
          },
          {
            "type": "p",
            "html": "Since 3.12, list, dict and set comprehensions are <em>inlined</em> (PEP 709): instead of building and calling a hidden function, the compiler emits the loop directly into the enclosing function, which makes them up to twice as fast. Generator expressions still get their own code object, because they must be able to pause."
          },
          {
            "type": "code",
            "src": "import dis\n\ndef squares(n):\n    return [i * i for i in range(n)]\n\nops = {ins.opname for ins in dis.get_instructions(squares)}\nprint(\"calls a hidden function:\", \"CALL\" in ops and \"MAKE_FUNCTION\" in ops)\nprint(\"loops in place:         \", \"FOR_ITER\" in ops)",
            "label": null,
            "output": "calls a hidden function: False\nloops in place:          True",
            "isError": false
          }
        ]
      },
      {
        "title": "The specializing adaptive interpreter",
        "body": [
          {
            "type": "p",
            "html": "Python 3.11 made the evaluation loop adaptive (PEP 659). Each generic instruction watches the types it actually sees. After a few executions with the same types it rewrites itself in place into a specialized version with a fast path and a cheap guard. If the guard ever fails, it falls back and may re-specialize."
          },
          {
            "type": "code",
            "src": "import dis\n\ndef add_all(values):\n    total = 0\n    for v in values:\n        total = total + v\n    return total\n\nfor _ in range(100):\n    add_all([1, 2, 3])\n\nfor ins in dis.get_instructions(add_all, adaptive=True):\n    if ins.opname.startswith((\"BINARY_OP\", \"FOR_ITER\")):\n        print(ins.opname)",
            "label": "after warming up on ints and lists",
            "output": "FOR_ITER_LIST\nBINARY_OP_ADD_INT",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>BINARY_OP</code> became an int-only add and <code>FOR_ITER</code> became a list-only iterator. Code that keeps its types stable &mdash; a variable is always an int, an attribute is always found in the same place &mdash; stays on these fast paths. Code that mixes types in one hot spot keeps falling back to the generic version."
          },
          {
            "type": "p",
            "html": "Later releases build on this: 3.13 added an experimental copy-and-patch JIT (off by default), and 3.14 can build the interpreter as a chain of tail calls for a further speed-up on supported compilers."
          }
        ]
      },
      {
        "title": ".pyc files",
        "body": [
          {
            "type": "p",
            "html": "Compiling is not free, so when a module is imported CPython caches the code object in <code>__pycache__/name.cpython-314.pyc</code>. The file is a 16-byte header followed by the marshalled code object."
          },
          {
            "type": "code",
            "src": "import importlib.util, marshal, pathlib, py_compile, struct, tempfile\n\nwith tempfile.TemporaryDirectory() as d:\n    src = pathlib.Path(d, \"mod.py\")\n    src.write_text(\"def hello():\\n    return 'hi'\\n\")\n    pyc = pathlib.Path(py_compile.compile(str(src), cfile=str(src) + \"c\"))\n    data = pyc.read_bytes()\n\nprint(\"magic matches this interpreter:\", data[:4] == importlib.util.MAGIC_NUMBER)\nflags, = struct.unpack(\"<I\", data[4:8])\nprint(\"flags (0 = invalidate by timestamp):\", flags)\ncode_obj = marshal.loads(data[16:])\nprint(\"module constants:\", [type(c).__name__ for c in code_obj.co_consts])",
            "label": null,
            "output": "magic matches this interpreter: True\nflags (0 = invalidate by timestamp): 0\nmodule constants: ['code', 'NoneType']",
            "isError": false
          },
          {
            "type": "p",
            "html": "The magic number changes whenever the bytecode format changes, so a <code>.pyc</code> from another version is ignored. The rest of the header is either the source&rsquo;s modification time and size, or (PEP 552) a hash of the source &mdash; useful for reproducible builds."
          },
          {
            "type": "note",
            "text": "A <code>.pyc</code> only saves compile time at import. It does not make the code run any faster once loaded, and the main script you run directly is never cached."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Is Python compiled or interpreted?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Both, and saying only one is the wrong answer. CPython compiles source to bytecode ahead of execution (and caches it as <code>.pyc</code>), then interprets that bytecode in a virtual machine. Syntax errors anywhere in a file are reported before the first line runs, which proves the compile step exists:"
          },
          {
            "type": "code",
            "src": "source = \"\"\"\nprint(\"first line\")\ndef broken(:\n    pass\n\"\"\"\ntry:\n    exec(compile(source, \"demo.py\", \"exec\"))\nexcept SyntaxError as e:\n    print(\"SyntaxError on line\", e.lineno, \"- and nothing printed\")",
            "label": null,
            "output": "SyntaxError on line 3 - and nothing printed",
            "isError": false
          },
          {
            "type": "p",
            "html": "PyPy goes further and JIT-compiles hot loops to machine code; CPython 3.13+ has an experimental JIT too. &ldquo;Interpreted&rdquo; describes an implementation, not the language."
          }
        ]
      },
      {
        "q": "Why does this raise <code>UnboundLocalError</code> instead of printing 10?",
        "level": "medium",
        "answer": [
          {
            "type": "code",
            "src": "count = 10\ndef report():\n    print(count)\n    count += 1\nreport()",
            "label": null,
            "output": "Traceback (most recent call last):\n  File \"bytecode_q1_0.py\", line 5, in <module>\n    report()\n    ~~~~~~^^\n  File \"bytecode_q1_0.py\", line 3, in report\n    print(count)\n          ^^^^^\nUnboundLocalError: cannot access local variable 'count' where it is not associated with a value",
            "isError": true
          },
          {
            "type": "p",
            "html": "Scope is decided by the compiler, for the whole function, before it runs. Because <code>count</code> is assigned somewhere in <code>report</code>, it is a local variable everywhere in <code>report</code>, and the compiler emits <code>LOAD_FAST</code> for the <code>print</code> line too. At run time that slot is still empty. Fix it with <code>global count</code> (or <code>nonlocal</code> in a closure) &mdash; or better, pass the value in and return the new one."
          }
        ]
      },
      {
        "q": "What does <code>a, b = b, a</code> compile to? Is a tuple created?",
        "level": "hard",
        "answer": [
          {
            "type": "code",
            "src": "import dis\ndef swap(a, b):\n    a, b = b, a\n    return a, b\ndis.dis(swap)",
            "label": null,
            "output": "  2           RESUME                   0\n\n  3           LOAD_FAST_LOAD_FAST     16 (b, a)\n              STORE_FAST_STORE_FAST   16 (b, a)\n\n  4           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)\n              BUILD_TUPLE              2\n              RETURN_VALUE",
            "isError": false
          },
          {
            "type": "p",
            "html": "No tuple is built. The compiler pushes <code>b</code> then <code>a</code> onto the stack and pops them straight back into the targets &mdash; the top of the stack (old <code>a</code>) goes into <code>b</code>, the next (old <code>b</code>) into <code>a</code>. Older versions pushed in source order and inserted a <code>ROT_TWO</code> or <code>SWAP</code> instruction; 3.14 simply reorders the stores so no swap is needed."
          },
          {
            "type": "p",
            "html": "What makes it safe is the language rule underneath: the whole right-hand side is evaluated before any name is assigned. The optimisation only applies to two or three targets &mdash; with four or more, CPython really does <code>BUILD_TUPLE</code> and <code>UNPACK_SEQUENCE</code>."
          }
        ]
      },
      {
        "q": "Why can the same integer literal give <code>is</code> = <code>True</code> in a script and <code>False</code> in the REPL?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "In a script the whole module is compiled in one go, and equal constants in one compilation are stored once, so both names get the same object. In the REPL each line you type is compiled separately, so each <code>1000</code> is its own constant and its own object."
          },
          {
            "type": "code",
            "src": "ns = {}\nexec(compile(\"a = 1000\\nb = 1000\", \"<one unit>\", \"exec\"), ns)\nprint(\"one compile:  \", ns[\"a\"] is ns[\"b\"])\n\nns = {}\nexec(compile(\"a = 1000\", \"<line 1>\", \"exec\"), ns)\nexec(compile(\"b = 1000\", \"<line 2>\", \"exec\"), ns)\nprint(\"two compiles: \", ns[\"a\"] is ns[\"b\"])",
            "label": null,
            "output": "one compile:   True\ntwo compiles:  False",
            "isError": false
          },
          {
            "type": "p",
            "html": "Neither result is guaranteed by the language &mdash; which is the real answer. Use <code>==</code> for values."
          }
        ]
      },
      {
        "q": "What is in a <code>.pyc</code> file, when is it regenerated, and does it make code faster?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A 16-byte header (magic number, flags, then either source mtime+size or a source hash) followed by the marshalled module code object. On import, CPython compares the header with the current source; if the magic number or timestamp does not match, it recompiles and rewrites the file."
          },
          {
            "type": "p",
            "html": "It only speeds up <em>import</em>, by skipping parsing and compiling. Execution speed is identical. The script you run directly (<code>python app.py</code>) is compiled every time and never cached; only imported modules are."
          }
        ]
      },
      {
        "q": "What is the specializing adaptive interpreter, and how should it change the way you write hot code?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Since 3.11 (PEP 659), generic instructions like <code>LOAD_ATTR</code>, <code>BINARY_OP</code> and <code>CALL</code> record the types they see and rewrite themselves into specialized versions &mdash; for example <code>LOAD_ATTR_INSTANCE_VALUE</code>, which reads an attribute at a known offset after a single type-version check. It is why 3.11 was 10&ndash;60% faster than 3.10 on typical code."
          },
          {
            "type": "p",
            "html": "The practical rule is <em>type stability</em>: keep the types flowing through a hot spot consistent. A function that sometimes gets ints and sometimes floats, or instances whose attributes are added in different orders, keeps de-specializing. Micro-tricks like caching globals in locals matter much less than they did."
          },
          {
            "type": "code",
            "src": "import dis\n\ndef add(a, b):\n    return a + b\n\nfor _ in range(100):\n    add(1.5, 2.5)\nprint([i.opname for i in dis.get_instructions(add, adaptive=True) if \"BINARY\" in i.opname])",
            "label": "specialized for floats",
            "output": "['BINARY_OP_ADD_FLOAT']",
            "isError": false
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: dis — Disassembler for Python bytecode",
        "url": "https://docs.python.org/3/library/dis.html"
      },
      {
        "label": "PEP 659 — Specializing adaptive interpreter",
        "url": "https://peps.python.org/pep-0659/"
      },
      {
        "label": "PEP 709 — Inlined comprehensions",
        "url": "https://peps.python.org/pep-0709/"
      },
      {
        "label": "CPython internals: the bytecode interpreter",
        "url": "https://github.com/python/cpython/blob/main/InternalDocs/interpreter.md"
      }
    ]
  },
  {
    "id": "object-model",
    "title": "The Python Object Model",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "&ldquo;Everything is an object&rdquo; is usually said and not explained. It means something precise: integers, strings, functions, classes, modules, even <code>type</code> itself are all values of the same basic C structure, each with an identity, a type, and a value. They can all be assigned to names, stored in containers, passed around and inspected.",
      "Once that is internalised, a lot of Python stops being magic. Decorators are just functions receiving functions. Classes are just objects created at run time. <code>len(x)</code> is just a call to a method found on <code>x</code>&rsquo;s type."
    ],
    "sections": [
      {
        "title": "Identity, type and value",
        "body": [
          {
            "type": "p",
            "html": "Every object has three things. <strong>Identity</strong> never changes while the object lives &mdash; <code>id()</code> returns it, <code>is</code> compares it. <strong>Type</strong> decides what operations the object supports and also never changes in practice. <strong>Value</strong> is what <code>==</code> compares, and may or may not be mutable."
          },
          {
            "type": "code",
            "src": "a = [1, 2, 3]\nb = [1, 2, 3]\nc = a\n\nprint(\"a == b:\", a == b)    # same value\nprint(\"a is b:\", a is b)    # different objects\nprint(\"a is c:\", a is c)    # two names, one object\n\nc.append(4)\nprint(\"a:\", a)              # changed through c\nprint(type(a), type(len), type(3.5))",
            "label": null,
            "output": "a == b: True\na is b: False\na is c: True\na: [1, 2, 3, 4]\n<class 'list'> <class 'builtin_function_or_method'> <class 'float'>",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Operator",
              "Compares",
              "Can be overridden",
              "Use for"
            ],
            "rows": [
              [
                "<code>is</code>",
                "Identity (same object)",
                "No",
                "<code>None</code>, sentinels, singletons"
              ],
              [
                "<code>==</code>",
                "Value, via <code>__eq__</code>",
                "Yes",
                "Everything else"
              ]
            ]
          }
        ]
      },
      {
        "title": "Functions are objects",
        "body": [
          {
            "type": "p",
            "html": "<code>def</code> is an executable statement. When it runs it creates a function object and binds it to a name. That object has a type, attributes, and can be stored and passed like any other value."
          },
          {
            "type": "code",
            "src": "def greet(name, punctuation=\"!\"):\n    \"\"\"Say hello.\"\"\"\n    return f\"hello {name}{punctuation}\"\n\nprint(type(greet).__name__)\nprint(greet.__name__, \"|\", greet.__doc__, \"|\", greet.__defaults__)\n\nsay = greet                     # another name, same object\nprint(say(\"ann\"))\n\nhandlers = {\"hi\": greet, \"shout\": str.upper}\nprint(handlers[\"shout\"](\"quiet\"))\n\ngreet.calls = 0                 # functions have a __dict__ too\ngreet.calls += 1\nprint(greet.__dict__)",
            "label": null,
            "output": "function\ngreet | Say hello. | ('!',)\nhello ann!\nQUIET\n{'calls': 1}",
            "isError": false
          },
          {
            "type": "p",
            "html": "Because functions are values you can return them from other functions. The inner function keeps access to the outer function&rsquo;s variables through <em>closure cells</em>, which is the foundation of decorators and callbacks."
          },
          {
            "type": "code",
            "src": "def multiplier(factor):\n    def apply(x):\n        return x * factor\n    return apply\n\ndouble, triple = multiplier(2), multiplier(3)\nprint(double(5), triple(5))\nprint(double.__closure__[0].cell_contents)\nprint(double.__code__ is triple.__code__)   # shared code, separate closures",
            "label": null,
            "output": "10 15\n2\nTrue",
            "isError": false
          }
        ]
      },
      {
        "title": "Classes are objects too",
        "body": [
          {
            "type": "p",
            "html": "<code>class</code> is also an executable statement. It runs the class body, then calls a <em>metaclass</em> &mdash; <code>type</code> by default &mdash; to build a new object: the class. So a class has a type, can be passed to functions, stored in dicts, and created on the fly."
          },
          {
            "type": "code",
            "src": "class Dog:\n    sound = \"woof\"\n    def speak(self):\n        return self.sound\n\nprint(type(Dog))\nprint(Dog.__name__, Dog.__bases__)\n\ndef build(cls):                 # a class passed as an argument\n    return cls()\nprint(build(Dog).speak())\n\nCat = type(\"Cat\", (), {\"sound\": \"meow\", \"speak\": lambda self: self.sound})\nprint(type(Cat), Cat().speak())",
            "label": null,
            "output": "<class 'type'>\nDog (<class 'object'>,)\nwoof\n<class 'type'> meow",
            "isError": false
          },
          {
            "type": "p",
            "html": "The three-argument <code>type(name, bases, namespace)</code> call is exactly what a <code>class</code> statement does after running the body. The two classes above are built the same way."
          }
        ]
      },
      {
        "title": "type and object: the knot at the top",
        "body": [
          {
            "type": "p",
            "html": "Two built-ins hold the whole system together. <code>object</code> is the base of every class. <code>type</code> is the class of every class. And they refer to each other:"
          },
          {
            "type": "code",
            "src": "print(type(object))            # object is an instance of type\nprint(type(type))              # type is an instance of itself\nprint(type.__bases__)          # type is a subclass of object\nprint(object.__bases__)        # object has no base\n\nprint(isinstance(type, object), isinstance(object, type))\nprint(isinstance(3, object), isinstance(int, type))",
            "label": null,
            "output": "<class 'type'>\n<class 'type'>\n(<class 'object'>,)\n()\nTrue True\nTrue True",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Relationship",
              "Question it answers",
              "Check with"
            ],
            "rows": [
              [
                "instance-of",
                "What made this object?",
                "<code>type(x)</code>, <code>isinstance</code>"
              ],
              [
                "subclass-of",
                "What does this class inherit from?",
                "<code>C.__bases__</code>, <code>C.__mro__</code>, <code>issubclass</code>"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Keep the two relationships apart and the diagram is simple: every class is a subclass of <code>object</code>; every class is an instance of <code>type</code> (or of a metaclass that subclasses <code>type</code>). The loop &mdash; <code>type</code> being its own type &mdash; is wired up in C at start-up."
          }
        ]
      },
      {
        "title": "Where attributes live",
        "body": [
          {
            "type": "p",
            "html": "Instances and classes each have a <code>__dict__</code>. Reading <code>obj.attr</code> checks the instance first, then the class and its bases. Writing <code>obj.attr = v</code> always writes to the instance, which <em>shadows</em> the class attribute rather than changing it."
          },
          {
            "type": "code",
            "src": "class Config:\n    retries = 3\n    tags = []                  # shared by every instance!\n\na, b = Config(), Config()\na.retries = 5                  # creates an instance attribute\na.tags.append(\"prod\")          # mutates the shared class list\n\nprint(vars(a), vars(b))\nprint(a.retries, b.retries, Config.retries)\nprint(b.tags)                  # b never touched tags",
            "label": null,
            "output": "{'retries': 5} {}\n5 3 3\n['prod']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Rebinding and mutating look similar and behave completely differently. <code>a.retries = 5</code> adds a key to <code>a.__dict__</code>. <code>a.tags.append(...)</code> reads <code>tags</code> (found on the class) and mutates that one shared list. Mutable defaults belong in <code>__init__</code>."
          },
          {
            "type": "note",
            "text": "The full lookup order also involves descriptors &mdash; which is how methods, <code>property</code> and <code>__slots__</code> work. That is the next topic."
          }
        ]
      },
      {
        "title": "Special methods are looked up on the type",
        "body": [
          {
            "type": "p",
            "html": "Operators and built-ins such as <code>len</code>, <code>+</code>, <code>iter</code> and <code>str</code> do not call <code>obj.__len__</code>. They call <code>type(obj).__len__(obj)</code>, skipping the instance entirely. That is faster, and it stops an instance from redefining what an operator means for itself."
          },
          {
            "type": "code",
            "src": "class Box:\n    def __init__(self, items):\n        self.items = items\n    def __len__(self):\n        return len(self.items)\n\nb = Box([1, 2, 3])\nb.__len__ = lambda: 99         # instance attribute\n\nprint(b.__len__())             # normal attribute lookup finds it\nprint(len(b))                  # len() goes to the type",
            "label": null,
            "output": "99\n3",
            "isError": false
          },
          {
            "type": "p",
            "html": "This also explains why you cannot make <code>len</code> work on a class by giving the class a <code>__len__</code>: <code>len(Box)</code> looks on <code>type(Box)</code>, which is the metaclass."
          },
          {
            "type": "code",
            "src": "class Sized(type):\n    def __len__(cls):\n        return 42\n\nclass Thing(metaclass=Sized):\n    pass\n\nprint(len(Thing))",
            "label": null,
            "output": "42",
            "isError": false
          }
        ]
      },
      {
        "title": "Equality, hashing and identity",
        "body": [
          {
            "type": "p",
            "html": "Objects used as dict keys or set members must be <em>hashable</em>, and equal objects must have equal hashes. By default, an instance compares and hashes by identity. Define <code>__eq__</code> and Python sets <code>__hash__</code> to <code>None</code>, because the old identity hash would now break the rule."
          },
          {
            "type": "code",
            "src": "class Point:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n    def __eq__(self, other):\n        return (self.x, self.y) == (other.x, other.y)\n\nprint(Point(1, 2) == Point(1, 2))\nprint(Point.__hash__)\ntry:\n    {Point(1, 2)}\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "True\nNone\nTypeError: cannot use 'Point' as a set element (unhashable type: 'Point')",
            "isError": false
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Point:\n    x: int\n    y: int\n\np = Point(1, 2)\nprint({p: \"origin-ish\"}[Point(1, 2)])\ntry:\n    p.x = 5\nexcept Exception as e:\n    print(type(e).__name__)",
            "label": "the usual fix: an immutable value type",
            "output": "origin-ish\nFrozenInstanceError",
            "isError": false
          },
          {
            "type": "p",
            "html": "Only make an object hashable if the fields in its hash cannot change. A mutable object whose hash changes after it is put in a set gets lost in the wrong bucket."
          }
        ]
      },
      {
        "title": "Callables",
        "body": [
          {
            "type": "p",
            "html": "Anything whose type defines <code>__call__</code> can be called. Functions, methods, classes (calling a class makes an instance), and your own objects:"
          },
          {
            "type": "code",
            "src": "class Counter:\n    def __init__(self):\n        self.n = 0\n    def __call__(self, step=1):\n        self.n += step\n        return self.n\n\ntick = Counter()\ntick(); tick(); print(tick(10))\n\nthings = {\"len\": len, \"Counter\": Counter, \"tick\": tick, \"'text'\": \"text\", \"42\": 42}\nfor label, thing in things.items():\n    print(f\"{label:8} callable={callable(thing)}\")",
            "label": null,
            "output": "12\nlen      callable=True\nCounter  callable=True\ntick     callable=True\n'text'   callable=False\n42       callable=False",
            "isError": false
          },
          {
            "type": "p",
            "html": "A callable object is a function that carries state in plain attributes. It is an alternative to a closure and is easier to inspect and test."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What does <code>type(type)</code> return, and how can that be?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It returns <code>type</code>. Every class is an instance of a metaclass, and <code>type</code> is the default metaclass &mdash; including for itself. It cannot be built by the usual rule (you would need <code>type</code> to exist before creating <code>type</code>), so CPython creates both <code>type</code> and <code>object</code> statically in C and links them together: <code>type</code> is an instance of <code>type</code> and a subclass of <code>object</code>; <code>object</code> is an instance of <code>type</code> and has no base."
          }
        ]
      },
      {
        "q": "Why does assigning <code>obj.__len__ = ...</code> not change what <code>len(obj)</code> returns?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Implicit special-method lookup bypasses the instance and goes straight to the type: <code>len(obj)</code> is <code>type(obj).__len__(obj)</code>. That makes built-in operations faster (one slot lookup in C, no dict check) and prevents surprising per-instance operator behaviour. To change it, change the class &mdash; or, for a class object itself, its metaclass."
          }
        ]
      },
      {
        "q": "A teammate adds <code>__eq__</code> to a class and now instances can&rsquo;t go in a set. Why, and what is the correct fix?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The rule is <em>a == b implies hash(a) == hash(b)</em>. The default hash is based on identity, which would break that rule once equality is by value, so Python sets <code>__hash__ = None</code> whenever a class defines <code>__eq__</code> without <code>__hash__</code>."
          },
          {
            "type": "p",
            "html": "The fix depends on whether the object is mutable. If it is a value that should never change, make it immutable and hash the same fields you compare &mdash; <code>@dataclass(frozen=True)</code> does both. If it is mutable, it should <em>not</em> be hashable: changing a field after insertion would leave it in the wrong hash bucket, and lookups would silently fail."
          },
          {
            "type": "code",
            "src": "class Key:\n    def __init__(self, v): self.v = v\n    def __eq__(self, o): return self.v == o.v\n    def __hash__(self): return hash(self.v)      # mutable AND hashable: a trap\n\nk = Key(1)\ns = {k}\nk.v = 2\nprint(k in s)             # the set looks in the bucket for hash(2)\nprint(any(x is k for x in s))",
            "label": null,
            "output": "False\nTrue",
            "isError": false
          }
        ]
      },
      {
        "q": "Explain the output of this code.",
        "level": "medium",
        "answer": [
          {
            "type": "code",
            "src": "class Team:\n    members = []\n    def join(self, name):\n        self.members.append(name)\n\nred, blue = Team(), Team()\nred.join(\"ann\")\nblue.join(\"bob\")\nprint(red.members, blue.members, red.members is blue.members)",
            "label": null,
            "output": "['ann', 'bob'] ['ann', 'bob'] True",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>members</code> is a class attribute: one list, created once when the class body ran. <code>self.members</code> finds no instance attribute, falls back to the class, and appends to the shared list. Both teams end up with both people. Create per-instance state in <code>__init__</code> (<code>self.members = []</code>). The same trap exists for mutable default arguments, for the same reason: the value is created once, at definition time."
          }
        ]
      },
      {
        "q": "Create a class with a method and a class attribute without using the <code>class</code> keyword.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Call the metaclass directly with a name, a tuple of bases and a namespace dict. Methods are just functions in that dict; they become bound methods on access, exactly as with a normal class."
          },
          {
            "type": "code",
            "src": "def __init__(self, name):\n    self.name = name\n\ndef greet(self):\n    return f\"{self.greeting}, {self.name}\"\n\nPerson = type(\"Person\", (object,), {\n    \"greeting\": \"hello\",\n    \"__init__\": __init__,\n    \"greet\": greet,\n})\n\nStudent = type(\"Student\", (Person,), {\"greeting\": \"hey\"})\n\nprint(Person(\"ann\").greet(), \"|\", Student(\"bob\").greet())\nprint(Student.__mro__)",
            "label": null,
            "output": "hello, ann | hey, bob\n(<class '__main__.Student'>, <class '__main__.Person'>, <class 'object'>)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Real uses: generating classes from a schema (ORMs, serializers, test parametrisation). <code>types.new_class</code> is the more complete version that also honours <code>__prepare__</code> and keyword arguments like <code>metaclass=</code>."
          }
        ]
      },
      {
        "q": "What is the difference between <code>is</code> and <code>==</code>, and when is <code>is</code> the right choice?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>is</code> checks identity and cannot be overridden. <code>==</code> calls <code>__eq__</code>, which a class can define however it likes. Use <code>is</code> only for singletons &mdash; <code>None</code>, <code>True</code>/<code>False</code>, <code>Ellipsis</code>, and your own sentinel objects &mdash; where identity <em>is</em> the meaning. Using it on numbers or strings seems to work because of caching and interning, and then fails on other values."
          },
          {
            "type": "code",
            "src": "import math\n\nnan = float(\"nan\")\nprint(nan == nan, nan is nan)            # NaN is not equal to itself\nprint(nan in [nan])                      # containers check identity first\n\nMISSING = object()                       # a sentinel only 'is' can match\ndef get(d, key, default=MISSING):\n    value = d.get(key, MISSING)\n    if value is MISSING:\n        return \"missing\" if default is MISSING else default\n    return value\nprint(get({\"a\": None}, \"a\"), get({}, \"a\"))",
            "label": null,
            "output": "False True\nTrue\nNone missing",
            "isError": false
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: Data model",
        "url": "https://docs.python.org/3/reference/datamodel.html"
      },
      {
        "label": "Python docs: Special method lookup",
        "url": "https://docs.python.org/3/reference/datamodel.html#special-method-lookup"
      },
      {
        "label": "Python docs: __hash__",
        "url": "https://docs.python.org/3/reference/datamodel.html#object.__hash__"
      }
    ]
  },
  {
    "id": "dunder-methods",
    "title": "Magic (Dunder) Methods",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "Methods whose names start and end with a double underscore &mdash; <code>__init__</code>, <code>__len__</code>, <code>__add__</code> &mdash; are called <em>special</em>, <em>magic</em> or <em>dunder</em> methods. You rarely call them yourself. Python calls them for you when you use syntax or a built-in: <code>a + b</code>, <code>len(x)</code>, <code>x[i]</code>, <code>for v in x</code>, <code>with x:</code>, <code>f\"{x}\"</code>.",
      "Together they are Python&rsquo;s <em>data model</em>: the protocol a class implements to plug into the language. A class that defines the right handful of dunders behaves like a built-in type, works with the standard library, and needs no special API of its own. This topic walks through the families of dunders, what each one is for, and the rules that are easy to get wrong."
    ],
    "sections": [
      {
        "title": "The mapping from syntax to dunder",
        "body": [
          {
            "type": "p",
            "html": "Every operator and many built-ins translate to a method call on the <em>type</em> of the object. Knowing the translation is most of the topic:"
          },
          {
            "type": "table",
            "head": [
              "You write",
              "Python calls",
              "Family"
            ],
            "rows": [
              [
                "<code>C(a)</code>",
                "<code>C.__new__(C, a)</code>, then <code>obj.__init__(a)</code>",
                "Lifecycle"
              ],
              [
                "<code>repr(x)</code>, <code>str(x)</code>, <code>f\"{x:spec}\"</code>",
                "<code>__repr__</code>, <code>__str__</code>, <code>__format__</code>",
                "Representation"
              ],
              [
                "<code>a == b</code>, <code>a &lt; b</code>",
                "<code>__eq__</code>, <code>__lt__</code> (and friends)",
                "Comparison"
              ],
              [
                "<code>hash(x)</code>, <code>bool(x)</code>",
                "<code>__hash__</code>, <code>__bool__</code> (fallback <code>__len__</code>)",
                "Hashing / truth"
              ],
              [
                "<code>a + b</code>, <code>a += b</code>, <code>-a</code>",
                "<code>__add__</code>/<code>__radd__</code>, <code>__iadd__</code>, <code>__neg__</code>",
                "Arithmetic"
              ],
              [
                "<code>len(x)</code>, <code>x[k]</code>, <code>k in x</code>",
                "<code>__len__</code>, <code>__getitem__</code>, <code>__contains__</code>",
                "Containers"
              ],
              [
                "<code>for v in x</code>, <code>next(it)</code>",
                "<code>__iter__</code>, <code>__next__</code>",
                "Iteration"
              ],
              [
                "<code>x.attr</code>, <code>x.attr = v</code>",
                "<code>__getattribute__</code>/<code>__getattr__</code>, <code>__setattr__</code>",
                "Attribute access"
              ],
              [
                "<code>x(...)</code>",
                "<code>__call__</code>",
                "Callables"
              ],
              [
                "<code>with x:</code>",
                "<code>__enter__</code>, <code>__exit__</code>",
                "Context managers"
              ],
              [
                "<code>int(x)</code>, <code>round(x)</code>, <code>seq[x]</code>",
                "<code>__int__</code>, <code>__round__</code>, <code>__index__</code>",
                "Conversion"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The lookup happens on the type, not the instance: <code>len(x)</code> is effectively <code>type(x).__len__(x)</code>. The object model topic shows why assigning <code>x.__len__ = ...</code> on an instance has no effect on <code>len(x)</code>."
          },
          {
            "type": "note",
            "text": "Only implement dunders Python already defines. Inventing your own <code>__names__</code> is reserved for the language and may collide with a future version."
          }
        ]
      },
      {
        "title": "Lifecycle: __new__, __init__, __del__",
        "body": [
          {
            "type": "p",
            "html": "Calling a class runs two steps. <code>__new__</code> is a static method that <em>creates</em> and returns the object; <code>__init__</code> then <em>initialises</em> the object it was given and must return <code>None</code>. Almost every class only needs <code>__init__</code>. You need <code>__new__</code> when the object must be decided before it exists &mdash; subclassing an immutable type, caching instances, or returning a different object altogether."
          },
          {
            "type": "code",
            "src": "class Trace:\n    def __new__(cls, *args):\n        print(f\"__new__  cls={cls.__name__} args={args}\")\n        return super().__new__(cls)\n    def __init__(self, value):\n        print(f\"__init__ value={value}\")\n        self.value = value\n\nt = Trace(7)\nprint(t.value)",
            "label": null,
            "output": "__new__  cls=Trace args=(7,)\n__init__ value=7\n7",
            "isError": false
          },
          {
            "type": "p",
            "html": "Immutable built-ins like <code>int</code>, <code>str</code> and <code>tuple</code> have their value fixed by the time <code>__init__</code> runs, so a subclass that wants to change the value must do it in <code>__new__</code>:"
          },
          {
            "type": "code",
            "src": "class Celsius(float):\n    def __new__(cls, value):\n        if value < -273.15:\n            raise ValueError(\"below absolute zero\")\n        return super().__new__(cls, round(value, 1))\n\n    def __repr__(self):\n        return f\"{float(self)}°C\"\n\nprint(Celsius(21.456), Celsius(21.456) + 1)\ntry:\n    Celsius(-300)\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "21.5°C 22.5\nValueError: below absolute zero",
            "isError": false
          },
          {
            "type": "p",
            "html": "If <code>__new__</code> returns something that is not an instance of the class, <code>__init__</code> is skipped. That is how an instance cache works:"
          },
          {
            "type": "code",
            "src": "class Color:\n    _cache = {}\n    def __new__(cls, name):\n        if name not in cls._cache:\n            obj = super().__new__(cls)\n            obj.name = name\n            cls._cache[name] = obj\n        return cls._cache[name]\n\nprint(Color(\"red\") is Color(\"red\"), Color(\"red\") is Color(\"blue\"))",
            "label": null,
            "output": "True False",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>__del__</code> runs when the object is about to be destroyed. In CPython that is usually when the reference count hits zero, but it is not guaranteed to run promptly (reference cycles) or at all (interpreter shutdown), and exceptions raised inside it are only printed as warnings."
          },
          {
            "type": "code",
            "src": "class Resource:\n    def __init__(self, name):\n        self.name = name\n    def __del__(self):\n        print(f\"__del__ {self.name}\")\n\nr = Resource(\"a\")\ndel r                     # refcount hits zero: runs now in CPython\nprint(\"after del\")",
            "label": null,
            "output": "__del__ a\nafter del",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "Do not use <code>__del__</code> for cleanup that must happen. Use a context manager (<code>__enter__</code>/<code>__exit__</code>) or <code>weakref.finalize</code>."
          }
        ]
      },
      {
        "title": "Representation: __repr__, __str__, __format__",
        "body": [
          {
            "type": "p",
            "html": "<code>__repr__</code> is for developers: unambiguous, ideally valid Python that recreates the object. It is what the REPL, debuggers, logs and containers show. <code>__str__</code> is for end users; if a class does not define it, <code>str()</code> falls back to <code>__repr__</code>. <code>__format__</code> handles the part after the colon in an f-string."
          },
          {
            "type": "code",
            "src": "class Money:\n    def __init__(self, amount, currency=\"USD\"):\n        self.amount, self.currency = amount, currency\n\n    def __repr__(self):\n        return f\"Money({self.amount!r}, {self.currency!r})\"\n\n    def __str__(self):\n        return f\"{self.amount:,.2f} {self.currency}\"\n\n    def __format__(self, spec):\n        if spec == \"short\":\n            return f\"{self.amount:.0f}{self.currency[0]}\"\n        return format(str(self), spec)\n\nm = Money(1234.5)\nprint(repr(m))\nprint(str(m))\nprint([m])                    # containers use repr of their items\nprint(f\"{m}|{m!r}|{m:short}|{m:>16}|\")",
            "label": null,
            "output": "Money(1234.5, 'USD')\n1,234.50 USD\n[Money(1234.5, 'USD')]\n1,234.50 USD|Money(1234.5, 'USD')|1234U|    1,234.50 USD|",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Method",
              "Called by",
              "Audience",
              "Default"
            ],
            "rows": [
              [
                "<code>__repr__</code>",
                "<code>repr()</code>, REPL, containers, <code>!r</code>",
                "Developers",
                "<code>&lt;Money object at 0x...&gt;</code>"
              ],
              [
                "<code>__str__</code>",
                "<code>str()</code>, <code>print()</code>, <code>f\"{x}\"</code>",
                "Users",
                "Falls back to <code>__repr__</code>"
              ],
              [
                "<code>__format__</code>",
                "<code>format()</code>, <code>f\"{x:spec}\"</code>",
                "Users",
                "<code>str(self)</code>, only an empty spec allowed"
              ],
              [
                "<code>__bytes__</code>",
                "<code>bytes(x)</code>",
                "Wire formats",
                "<code>TypeError</code>"
              ]
            ]
          },
          {
            "type": "note",
            "text": "If you define only one, define <code>__repr__</code>. You get a useful <code>str()</code> for free."
          }
        ]
      },
      {
        "title": "Comparison and NotImplemented",
        "body": [
          {
            "type": "p",
            "html": "The six rich comparison methods are <code>__eq__</code>, <code>__ne__</code>, <code>__lt__</code>, <code>__le__</code>, <code>__gt__</code>, <code>__ge__</code>. When a method does not know how to compare with the other operand it should <em>return</em> <code>NotImplemented</code> (not raise). Python then tries the reflected method on the other object: <code>a &lt; b</code> falls back to <code>b &gt; a</code>, and <code>a == b</code> to <code>b == a</code>. If both give up, <code>==</code> falls back to identity and ordering raises <code>TypeError</code>."
          },
          {
            "type": "code",
            "src": "class Version:\n    def __init__(self, text):\n        self.parts = tuple(int(p) for p in text.split(\".\"))\n    def __repr__(self):\n        return \"Version(%r)\" % \".\".join(map(str, self.parts))\n    def __eq__(self, other):\n        if not isinstance(other, Version):\n            return NotImplemented\n        return self.parts == other.parts\n    def __lt__(self, other):\n        if not isinstance(other, Version):\n            return NotImplemented\n        return self.parts < other.parts\n\na, b = Version(\"1.10.0\"), Version(\"1.9.3\")\nprint(a == Version(\"1.10.0\"), a != b)   # __ne__ is derived from __eq__\nprint(a < b, a > b)                     # a > b becomes b < a\nprint(sorted([a, b, Version(\"0.1\")]))\nprint(a == \"1.10.0\")                    # both sides give up -> identity\ntry:\n    a <= b                              # no __le__ or __ge__ anywhere\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "True True\nFalse True\n[Version('0.1'), Version('1.9.3'), Version('1.10.0')]\nFalse\nTypeError: '<=' not supported between instances of 'Version' and 'Version'",
            "isError": false
          },
          {
            "type": "p",
            "html": "Writing all six is tedious. <code>functools.total_ordering</code> fills in the missing ones from <code>__eq__</code> plus one ordering method. <code>@dataclass(order=True)</code> generates all of them by comparing fields as a tuple."
          },
          {
            "type": "code",
            "src": "from functools import total_ordering\n\n@total_ordering\nclass Grade:\n    order = \"FDCBA\"\n    def __init__(self, letter):\n        self.letter = letter\n    def __eq__(self, other):\n        return self.letter == other.letter\n    def __lt__(self, other):\n        return self.order.index(self.letter) < self.order.index(other.letter)\n\na, c = Grade(\"A\"), Grade(\"C\")\nprint(a > c, a >= c, c <= a, max([c, a, Grade(\"B\")]).letter)",
            "label": null,
            "output": "True True True A",
            "isError": false
          }
        ]
      },
      {
        "title": "Hashing and truthiness: __hash__, __bool__",
        "body": [
          {
            "type": "p",
            "html": "<code>__hash__</code> must return an int, and objects that compare equal must hash equal. Defining <code>__eq__</code> without <code>__hash__</code> sets <code>__hash__</code> to <code>None</code>, making instances unhashable. Hash the same fields you compare, and only if those fields never change."
          },
          {
            "type": "code",
            "src": "class Point:\n    __slots__ = (\"x\", \"y\")\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n    def __eq__(self, other):\n        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)\n    def __hash__(self):\n        return hash((self.x, self.y))      # delegate to a tuple\n\nseen = {Point(1, 2), Point(1, 2), Point(3, 4)}\nprint(len(seen), Point(1, 2) in seen)",
            "label": null,
            "output": "2 True",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>bool(x)</code> (and every <code>if x:</code>) calls <code>__bool__</code>. If that is missing it uses <code>__len__</code> and treats zero as false. If both are missing, every instance is truthy."
          },
          {
            "type": "code",
            "src": "class Plain: pass\n\nclass Basket:\n    def __init__(self, *items): self.items = list(items)\n    def __len__(self): return len(self.items)\n\nclass Account:\n    def __init__(self, balance): self.balance = balance\n    def __bool__(self): return self.balance > 0\n\nprint(bool(Plain()), bool(Basket()), bool(Basket(\"egg\")))\nprint(bool(Account(0)), bool(Account(5)))\nprint(\"empty\" if not Basket() else \"has items\")",
            "label": null,
            "output": "True False True\nFalse True\nempty",
            "isError": false
          }
        ]
      },
      {
        "title": "Arithmetic: forward, reflected and in-place",
        "body": [
          {
            "type": "p",
            "html": "Each binary operator has three dunders. For <code>+</code>: <code>__add__</code> for <code>a + b</code>, <code>__radd__</code> (reflected) when the left operand gives up, and <code>__iadd__</code> for <code>a += b</code>. The rule for <code>a + b</code> is:"
          },
          {
            "type": "p",
            "html": "1. Call <code>a.__add__(b)</code>. If it returns <code>NotImplemented</code>&hellip;<br>2. call <code>b.__radd__(a)</code>. If that also returns <code>NotImplemented</code>, raise <code>TypeError</code>.<br>Exception: if <code>b</code>&rsquo;s type is a <em>subclass</em> of <code>a</code>&rsquo;s type and overrides the reflected method, <code>b.__radd__</code> is tried first."
          },
          {
            "type": "code",
            "src": "class Vector:\n    def __init__(self, *xs):\n        self.xs = tuple(xs)\n    def __repr__(self):\n        return f\"Vector{self.xs}\"\n\n    def __add__(self, other):\n        if isinstance(other, Vector):\n            return Vector(*(a + b for a, b in zip(self.xs, other.xs)))\n        return NotImplemented\n\n    def __mul__(self, k):\n        if isinstance(k, (int, float)):\n            return Vector(*(a * k for a in self.xs))\n        return NotImplemented\n    __rmul__ = __mul__                    # k * v is the same as v * k\n\n    def __matmul__(self, other):          # the @ operator: dot product\n        return sum(a * b for a, b in zip(self.xs, other.xs))\n\n    def __neg__(self):\n        return self * -1\n    def __abs__(self):\n        return sum(a * a for a in self.xs) ** 0.5\n\nv, w = Vector(3, 4), Vector(1, 1)\nprint(v + w, v * 2, 2 * v, -v)\nprint(v @ w, abs(v))\ntry:\n    v + 1\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "Vector(4, 5) Vector(6, 8) Vector(6, 8) Vector(-3, -4)\n7 5.0\nTypeError: unsupported operand type(s) for +: 'Vector' and 'int'",
            "isError": false
          },
          {
            "type": "p",
            "html": "Reflected methods are what let your type sit on the <em>right</em> of a built-in. <code>sum()</code> starts from <code>0</code>, so <code>0 + first_item</code> needs <code>__radd__</code>:"
          },
          {
            "type": "code",
            "src": "class Cents:\n    def __init__(self, n): self.n = n\n    def __repr__(self): return f\"Cents({self.n})\"\n    def __add__(self, other):\n        if isinstance(other, Cents):\n            return Cents(self.n + other.n)\n        if isinstance(other, int):\n            return Cents(self.n + other)\n        return NotImplemented\n    __radd__ = __add__\n\nprint(sum([Cents(5), Cents(10), Cents(20)]))",
            "label": null,
            "output": "Cents(35)",
            "isError": false
          },
          {
            "type": "p",
            "html": "In-place operators mutate when they can. If <code>__iadd__</code> is missing, <code>a += b</code> becomes <code>a = a + b</code> and rebinds the name to a new object. That is why <code>+=</code> changes a list in place but builds a new tuple:"
          },
          {
            "type": "code",
            "src": "class Bag:\n    def __init__(self): self.items = []\n    def __iadd__(self, item):\n        self.items.append(item)\n        return self                      # must return the result\n\nb = Bag(); before = id(b)\nb += \"apple\"; b += \"pear\"\nprint(b.items, id(b) == before)\n\nnums, tup = [1], (1,)\nn_id, t_id = id(nums), id(tup)\nnums += [2]; tup += (2,)\nprint(id(nums) == n_id, id(tup) == t_id)",
            "label": null,
            "output": "['apple', 'pear'] True\nTrue False",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Operator",
              "Forward",
              "Reflected",
              "In-place"
            ],
            "rows": [
              [
                "<code>+</code> <code>-</code> <code>*</code> <code>@</code>",
                "<code>__add__ __sub__ __mul__ __matmul__</code>",
                "<code>__radd__</code> &hellip;",
                "<code>__iadd__</code> &hellip;"
              ],
              [
                "<code>/</code> <code>//</code> <code>%</code> <code>**</code>",
                "<code>__truediv__ __floordiv__ __mod__ __pow__</code>",
                "<code>__rtruediv__</code> &hellip;",
                "<code>__itruediv__</code> &hellip;"
              ],
              [
                "<code>&lt;&lt;</code> <code>&gt;&gt;</code> <code>&amp;</code> <code>|</code> <code>^</code>",
                "<code>__lshift__ __rshift__ __and__ __or__ __xor__</code>",
                "<code>__rlshift__</code> &hellip;",
                "<code>__ilshift__</code> &hellip;"
              ],
              [
                "<code>divmod(a, b)</code>",
                "<code>__divmod__</code>",
                "<code>__rdivmod__</code>",
                "&mdash;"
              ],
              [
                "unary <code>-</code> <code>+</code> <code>~</code> <code>abs()</code>",
                "<code>__neg__ __pos__ __invert__ __abs__</code>",
                "&mdash;",
                "&mdash;"
              ]
            ]
          },
          {
            "type": "note",
            "text": "Return <code>NotImplemented</code> for types you do not handle, never raise <code>TypeError</code> yourself &mdash; raising stops Python from giving the other operand its turn."
          }
        ]
      },
      {
        "title": "Containers: __len__, __getitem__, __setitem__, __contains__",
        "body": [
          {
            "type": "p",
            "html": "A container protocol is a few dunders. <code>__getitem__</code> receives whatever is inside the brackets: an int, a key, or a <code>slice</code> object for <code>x[a:b:c]</code>. <code>__contains__</code> powers <code>in</code>; without it Python falls back to iterating."
          },
          {
            "type": "code",
            "src": "class Playlist:\n    def __init__(self, *songs):\n        self._songs = list(songs)\n    def __len__(self):\n        return len(self._songs)\n    def __getitem__(self, index):\n        if isinstance(index, slice):\n            return Playlist(*self._songs[index])\n        return self._songs[index]\n    def __setitem__(self, index, song):\n        self._songs[index] = song\n    def __delitem__(self, index):\n        del self._songs[index]\n    def __contains__(self, song):\n        return song.lower() in (s.lower() for s in self._songs)\n    def __repr__(self):\n        return f\"Playlist{tuple(self._songs)}\"\n\np = Playlist(\"Intro\", \"Verse\", \"Chorus\", \"Outro\")\nprint(len(p), p[0], p[-1], p[1:3])\np[0] = \"Overture\"; del p[-1]\nprint(p, \"chorus\" in p)\nprint(list(reversed(p)))       # works via __len__ + __getitem__",
            "label": null,
            "output": "4 Intro Outro Playlist('Verse', 'Chorus')\nPlaylist('Overture', 'Verse', 'Chorus') True\n['Chorus', 'Verse', 'Overture']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Notice that <code>reversed()</code> and even <code>for</code> loops work without <code>__iter__</code> or <code>__reversed__</code>: Python falls back to calling <code>__getitem__</code> with 0, 1, 2&hellip; until <code>IndexError</code>. That is the <em>old sequence protocol</em>; define <code>__iter__</code> for anything new."
          },
          {
            "type": "p",
            "html": "Mappings get one extra hook. A <code>dict</code> subclass can define <code>__missing__</code>, which <code>d[key]</code> calls for absent keys. This is how <code>collections.defaultdict</code> and <code>Counter</code> work:"
          },
          {
            "type": "code",
            "src": "class Inventory(dict):\n    def __missing__(self, key):\n        return 0                  # no KeyError, and nothing is stored\n\nstock = Inventory(apple=3)\nprint(stock[\"apple\"], stock[\"kiwi\"], \"kiwi\" in stock)\nprint(stock.get(\"kiwi\"))          # .get() does not call __missing__",
            "label": null,
            "output": "3 0 False\nNone",
            "isError": false
          }
        ]
      },
      {
        "title": "Iteration: __iter__ and __next__",
        "body": [
          {
            "type": "p",
            "html": "An <strong>iterable</strong> has <code>__iter__</code>, which returns an <strong>iterator</strong>. An iterator has <code>__next__</code>, which returns the next value or raises <code>StopIteration</code>, and an <code>__iter__</code> that returns itself. A <code>for</code> loop is <code>it = iter(x)</code> followed by <code>next(it)</code> until <code>StopIteration</code>."
          },
          {
            "type": "code",
            "src": "class Countdown:                    # an iterator: single use\n    def __init__(self, start):\n        self.current = start\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.current <= 0:\n            raise StopIteration\n        self.current -= 1\n        return self.current + 1\n\nc = Countdown(3)\nprint(list(c), list(c))             # exhausted after one pass",
            "label": null,
            "output": "[3, 2, 1] []",
            "isError": false
          },
          {
            "type": "p",
            "html": "Keep the iterable and the iterator separate so the object can be looped over more than once. Writing <code>__iter__</code> as a generator does exactly that with no <code>__next__</code> to maintain:"
          },
          {
            "type": "code",
            "src": "class Range2D:                      # an iterable: reusable\n    def __init__(self, rows, cols):\n        self.rows, self.cols = rows, cols\n    def __iter__(self):\n        for r in range(self.rows):\n            for c in range(self.cols):\n                yield (r, c)\n    def __reversed__(self):\n        return reversed(list(self))\n\ngrid = Range2D(2, 2)\nprint(list(grid))\nprint(list(grid))                   # a fresh generator each time\nprint(list(reversed(grid))[:2])",
            "label": null,
            "output": "[(0, 0), (0, 1), (1, 0), (1, 1)]\n[(0, 0), (0, 1), (1, 0), (1, 1)]\n[(1, 1), (1, 0)]",
            "isError": false
          },
          {
            "type": "note",
            "text": "Iterables return a <em>new</em> iterator from <code>__iter__</code>. Iterators return <code>self</code>. Mixing the two up is how you get a loop that silently runs zero times the second time."
          }
        ]
      },
      {
        "title": "Attribute access: __getattr__, __getattribute__, __setattr__",
        "body": [
          {
            "type": "p",
            "html": "Four hooks sit around <code>.</code> lookups. <code>__getattribute__</code> is called for <em>every</em> read. <code>__getattr__</code> is called only when normal lookup failed, which makes it the safe one to override. <code>__setattr__</code> and <code>__delattr__</code> intercept every write and delete."
          },
          {
            "type": "code",
            "src": "class Settings:\n    def __init__(self, **values):\n        # bypass our own __setattr__ while building\n        object.__setattr__(self, \"_values\", values)\n\n    def __getattr__(self, name):         # only for missing names\n        try:\n            return self._values[name]\n        except KeyError:\n            raise AttributeError(name) from None\n\n    def __setattr__(self, name, value):\n        raise AttributeError(f\"Settings are read-only: {name}\")\n\n    def __dir__(self):\n        return list(self._values)\n\ns = Settings(debug=True, workers=4)\nprint(s.debug, s.workers, dir(s))\nprint(getattr(s, \"timeout\", 30))         # default works: AttributeError\ntry:\n    s.debug = False\nexcept AttributeError as e:\n    print(\"AttributeError:\", e)",
            "label": null,
            "output": "True 4 ['debug', 'workers']\n30\nAttributeError: Settings are read-only: debug",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>__getattr__</code> must raise <code>AttributeError</code> for unknown names. Raising anything else breaks <code>getattr(obj, name, default)</code>, <code>hasattr</code> and copy/pickle, which all rely on that exception."
          },
          {
            "type": "p",
            "html": "A common real use is delegation: wrap an object and forward everything you do not override."
          },
          {
            "type": "code",
            "src": "class LoggingList:\n    def __init__(self):\n        self._inner = []\n    def append(self, item):\n        print(f\"append({item!r})\")\n        self._inner.append(item)\n    def __getattr__(self, name):         # everything else goes through\n        return getattr(self._inner, name)\n    def __len__(self):                   # dunders are NOT forwarded\n        return len(self._inner)\n\nlog = LoggingList()\nlog.append(3); log.append(1)\nlog.sort()\nprint(log._inner, log.index(3), len(log))",
            "label": null,
            "output": "append(3)\nappend(1)\n[1, 3] 1 2",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "<code>__getattr__</code> does not catch implicit dunder lookups: <code>len(log)</code> goes straight to <code>type(log).__len__</code>. A proxy must define every dunder it wants to forward."
          },
          {
            "type": "p",
            "html": "Overriding <code>__getattribute__</code> is rarely needed and easy to break: any <code>self.x</code> inside it calls itself again. Always reach the real value through <code>super().__getattribute__</code>."
          },
          {
            "type": "code",
            "src": "class Audited:\n    def __init__(self):\n        self.a, self.b = 1, 2\n    def __getattribute__(self, name):\n        if not name.startswith(\"_\"):\n            print(f\"read {name}\")\n        return super().__getattribute__(name)\n\nx = Audited()\nprint(x.a + x.b)",
            "label": null,
            "output": "read a\nread b\n3",
            "isError": false
          }
        ]
      },
      {
        "title": "Callables and context managers",
        "body": [
          {
            "type": "p",
            "html": "<code>__call__</code> makes instances callable, which is useful for objects that behave like functions but carry configuration or state. <code>__enter__</code> and <code>__exit__</code> make an object usable in a <code>with</code> block; the context managers topic covers them in full."
          },
          {
            "type": "code",
            "src": "import time\n\nclass Retry:\n    def __init__(self, times):\n        self.times = times\n    def __call__(self, fn, *args):\n        for attempt in range(1, self.times + 1):\n            try:\n                return fn(*args)\n            except ValueError as e:\n                print(f\"attempt {attempt} failed: {e}\")\n        raise RuntimeError(\"gave up\")\n\nclass Timer:\n    def __enter__(self):\n        self.start = time.perf_counter()\n        return self\n    def __exit__(self, exc_type, exc, tb):\n        self.elapsed = time.perf_counter() - self.start\n        print(f\"exit: exc_type={exc_type.__name__ if exc_type else None}\")\n        return False                   # do not swallow exceptions\n\ncalls = iter([ValueError(\"flaky\"), ValueError(\"flaky\"), \"ok\"])\ndef flaky():\n    r = next(calls)\n    if isinstance(r, Exception):\n        raise r\n    return r\n\nwith Timer() as t:\n    print(Retry(3)(flaky))\nprint(t.elapsed < 1)",
            "label": null,
            "output": "attempt 1 failed: flaky\nattempt 2 failed: flaky\nok\nexit: exc_type=None\nTrue",
            "isError": false
          }
        ]
      },
      {
        "title": "Conversion: __int__, __float__, __index__, __round__",
        "body": [
          {
            "type": "p",
            "html": "Conversion built-ins each have a dunder. The subtle one is <code>__index__</code>: it says &ldquo;this object <em>is</em> an integer&rdquo;, not merely &ldquo;can be turned into one&rdquo;. Only <code>__index__</code> lets an object be used as a list index, a slice bound, or passed to <code>bin()</code>/<code>hex()</code>. <code>float</code> has <code>__int__</code> but no <code>__index__</code>, which is why <code>[1, 2][1.0]</code> is an error."
          },
          {
            "type": "code",
            "src": "import math\n\nclass Fraction:\n    def __init__(self, num, den):\n        self.num, self.den = num, den\n    def __float__(self):\n        return self.num / self.den\n    def __int__(self):\n        return self.num // self.den\n    def __round__(self, ndigits=None):\n        return round(float(self), ndigits)\n    def __floor__(self):\n        return math.floor(self.num / self.den)\n    def __ceil__(self):\n        return math.ceil(self.num / self.den)\n\nclass Slot:\n    def __init__(self, n): self.n = n\n    def __index__(self): return self.n\n\nf = Fraction(22, 7)\nprint(float(f), int(f), round(f), round(f, 3), math.floor(f), math.ceil(f))\nprint([\"a\", \"b\", \"c\"][Slot(2)], bin(Slot(5)), \"xyz\"[:Slot(2)])\ntry:\n    [\"a\", \"b\"][f]\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "3.142857142857143 3 3 3.143 3 4\nc 0b101 xy\nTypeError: list indices must be integers or slices, not Fraction",
            "isError": false
          }
        ]
      },
      {
        "title": "Class-level hooks: __init_subclass__, __class_getitem__, __set_name__",
        "body": [
          {
            "type": "p",
            "html": "Some dunders are called on classes rather than instances. <code>__init_subclass__</code> runs on the parent whenever a subclass is created &mdash; a lightweight alternative to a metaclass for registries and validation. <code>__class_getitem__</code> handles <code>Cls[...]</code>, which is how <code>list[int]</code> works. <code>__set_name__</code> tells a descriptor the attribute name it was assigned to."
          },
          {
            "type": "code",
            "src": "class Plugin:\n    registry = {}\n    def __init_subclass__(cls, name=None, **kwargs):\n        super().__init_subclass__(**kwargs)\n        Plugin.registry[name or cls.__name__.lower()] = cls\n\nclass CSVExporter(Plugin, name=\"csv\"): pass\nclass JSONExporter(Plugin): pass\nprint(Plugin.registry)\n\nclass Box:\n    def __class_getitem__(cls, item):\n        return f\"{cls.__name__} of {item.__name__}\"\nprint(Box[int], list[int])\n\nclass Positive:\n    def __set_name__(self, owner, name):\n        self.name = \"_\" + name\n    def __get__(self, obj, owner):\n        return getattr(obj, self.name)\n    def __set__(self, obj, value):\n        if value <= 0:\n            raise ValueError(f\"{self.name[1:]} must be positive\")\n        setattr(obj, self.name, value)\n\nclass Order:\n    qty = Positive()\n    def __init__(self, qty): self.qty = qty\n\nprint(Order(3).qty)\ntry:\n    Order(0)\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "{'csv': <class '__main__.CSVExporter'>, 'jsonexporter': <class '__main__.JSONExporter'>}\nBox of int list[int]\n3\nValueError: qty must be positive",
            "isError": false
          },
          {
            "type": "note",
            "text": "<code>__get__</code>, <code>__set__</code> and <code>__delete__</code> are the descriptor protocol &mdash; the next topic explains how they drive methods and <code>property</code>."
          }
        ]
      },
      {
        "title": "Copying and pickling: __copy__, __deepcopy__, __reduce__",
        "body": [
          {
            "type": "p",
            "html": "<code>copy.copy</code> and <code>copy.deepcopy</code> work on most objects without help. Define <code>__copy__</code>/<code>__deepcopy__</code> when some state must not be duplicated &mdash; a cache, a lock, a connection &mdash; and <code>__getstate__</code>/<code>__setstate__</code> (or <code>__reduce__</code>) to control what pickle stores."
          },
          {
            "type": "code",
            "src": "import copy, pickle\n\nclass Model:\n    def __init__(self, weights):\n        self.weights = weights\n        self._cache = {}\n\n    def __deepcopy__(self, memo):\n        clone = Model(copy.deepcopy(self.weights, memo))\n        return clone                          # fresh, empty cache\n\n    def __getstate__(self):\n        state = self.__dict__.copy()\n        del state[\"_cache\"]                   # do not pickle the cache\n        return state\n    def __setstate__(self, state):\n        self.__dict__.update(state, _cache={})\n\nm = Model([1, 2])\nm._cache[\"warm\"] = True\nd = copy.deepcopy(m)\nd.weights.append(3)\nprint(m.weights, d.weights, d._cache)\n\np = pickle.loads(pickle.dumps(m))\nprint(p.weights, p._cache)",
            "label": null,
            "output": "[1, 2] [1, 2, 3] {}\n[1, 2] {}",
            "isError": false
          }
        ]
      },
      {
        "title": "Putting it together",
        "body": [
          {
            "type": "p",
            "html": "A small class that implements a dozen dunders feels completely native: it prints well, compares, hashes, sorts, iterates, supports arithmetic and <code>in</code>, and works with <code>sum</code>, <code>sorted</code>, <code>set</code>, <code>dict</code> and f-strings without a single custom method name."
          },
          {
            "type": "code",
            "src": "from functools import total_ordering\n\n@total_ordering\nclass Money:\n    __slots__ = (\"cents\",)\n    def __init__(self, cents): self.cents = cents\n    def __repr__(self): return f\"Money({self.cents})\"\n    def __str__(self): return f\"${self.cents / 100:,.2f}\"\n    def __eq__(self, o):\n        return isinstance(o, Money) and self.cents == o.cents\n    def __lt__(self, o):\n        if not isinstance(o, Money): return NotImplemented\n        return self.cents < o.cents\n    def __hash__(self): return hash(self.cents)\n    def __bool__(self): return self.cents != 0\n    def __add__(self, o):\n        if isinstance(o, Money): return Money(self.cents + o.cents)\n        if o == 0: return self\n        return NotImplemented\n    __radd__ = __add__\n    def __mul__(self, k):\n        if isinstance(k, int): return Money(self.cents * k)\n        return NotImplemented\n    __rmul__ = __mul__\n\nprices = [Money(1999), Money(500), Money(1999), Money(0)]\nprint(sum(prices), max(prices), sorted(set(prices)))\nprint(3 * Money(250), Money(100) >= Money(99), [p for p in prices if p])\nprint(f\"total: {sum(prices)}\")",
            "label": null,
            "output": "$44.98 $19.99 [Money(0), Money(500), Money(1999)]\n$7.50 True [Money(1999), Money(500), Money(1999)]\ntotal: $44.98",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What is the difference between <code>__new__</code> and <code>__init__</code>? When do you need <code>__new__</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>__new__</code> is an implicit static method that receives the class and <em>returns the new object</em>. <code>__init__</code> receives that object and fills it in; it must return <code>None</code>. <code>C(args)</code> is roughly <code>obj = C.__new__(C, args)</code>, then <code>obj.__init__(args)</code> if <code>obj</code> is an instance of <code>C</code>."
          },
          {
            "type": "p",
            "html": "You need <code>__new__</code> when the decision has to happen before the object exists: subclassing an immutable type (<code>int</code>, <code>str</code>, <code>tuple</code>) whose value is fixed at creation, returning a cached or singleton instance, or returning an object of a different class. Metaclasses also use <code>__new__</code> to build classes."
          },
          {
            "type": "code",
            "src": "class UpperStr(str):\n    def __new__(cls, value):\n        return super().__new__(cls, value.upper())\n    def __init__(self, value):\n        print(\"init sees\", repr(value), \"but self is\", repr(str(self)))\n\nprint(UpperStr(\"hello\"))",
            "label": null,
            "output": "init sees 'hello' but self is 'HELLO'\nHELLO",
            "isError": false
          }
        ]
      },
      {
        "q": "Why should <code>__add__</code> return <code>NotImplemented</code> instead of raising <code>TypeError</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Returning <code>NotImplemented</code> tells Python &ldquo;I do not handle this operand, ask the other side&rdquo;, so it goes on to try <code>other.__radd__(self)</code>. Raising <code>TypeError</code> ends the operation immediately, so another type that <em>does</em> know how to add itself to yours never gets asked. Python raises the <code>TypeError</code> for you once both sides have returned <code>NotImplemented</code>."
          },
          {
            "type": "code",
            "src": "class Strict:\n    def __add__(self, other):\n        raise TypeError(\"no\")\n\nclass Polite:\n    def __add__(self, other):\n        return NotImplemented\n\nclass Meters:\n    def __radd__(self, other):\n        return f\"Meters added to {type(other).__name__}\"\n\nprint(Polite() + Meters())\ntry:\n    Strict() + Meters()\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "Meters added to Polite\nTypeError: no",
            "isError": false
          },
          {
            "type": "p",
            "html": "Note that <code>NotImplemented</code> (a singleton value) and <code>NotImplementedError</code> (an exception for abstract methods) are different things."
          }
        ]
      },
      {
        "q": "What is the difference between <code>__getattr__</code> and <code>__getattribute__</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>__getattribute__</code> runs for every attribute read, before anything else, and is what implements normal lookup (instance dict, class, descriptors). <code>__getattr__</code> is only a fallback: Python calls it after normal lookup has raised <code>AttributeError</code>. Overriding <code>__getattr__</code> is safe and common (proxies, dynamic attributes). Overriding <code>__getattribute__</code> is rare, slows every access, and recurses infinitely if you read <code>self.anything</code> inside it without going through <code>super().__getattribute__</code>."
          },
          {
            "type": "code",
            "src": "class Demo:\n    x = 1\n    def __getattr__(self, name):\n        return f\"fallback for {name}\"\n\nd = Demo()\nprint(d.x, \"|\", d.y)",
            "label": null,
            "output": "1 | fallback for y",
            "isError": false
          }
        ]
      },
      {
        "q": "Explain the output: the class defines only <code>__getitem__</code>, yet <code>for</code>, <code>in</code> and <code>list()</code> all work.",
        "level": "hard",
        "answer": [
          {
            "type": "code",
            "src": "class Squares:\n    def __getitem__(self, i):\n        if i >= 5:\n            raise IndexError\n        print(f\"getitem({i})\", end=\" \")\n        return i * i\n\ns = Squares()\nprint(list(s))\nprint(9 in s)\nprint(hasattr(s, \"__iter__\"))",
            "label": null,
            "output": "getitem(0) getitem(1) getitem(2) getitem(3) getitem(4) [0, 1, 4, 9, 16]\ngetitem(0) getitem(1) getitem(2) getitem(3) True\nFalse",
            "isError": false
          },
          {
            "type": "p",
            "html": "When a type has no <code>__iter__</code>, <code>iter()</code> falls back to the legacy sequence protocol: it builds an iterator that calls <code>__getitem__(0)</code>, <code>__getitem__(1)</code>, &hellip; until <code>IndexError</code>. <code>in</code> without <code>__contains__</code> iterates and compares, stopping at the first match (so <code>getitem(4)</code> is never called for <code>9 in s</code>). This is why <code>collections.abc.Iterable</code> does not detect such classes &mdash; they have no <code>__iter__</code> &mdash; and why the reliable test for iterability is calling <code>iter(x)</code> and catching <code>TypeError</code>."
          }
        ]
      },
      {
        "q": "A proxy class forwards everything with <code>__getattr__</code>, but <code>len(proxy)</code> and <code>proxy[0]</code> fail. Why, and how do you fix it?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Implicit special method lookup (from operators and built-ins) goes directly to the type&rsquo;s slots and never touches <code>__getattr__</code> or <code>__getattribute__</code>. <code>proxy.__len__()</code> written explicitly would be forwarded; <code>len(proxy)</code> is not. The fix is to define the dunders on the proxy class &mdash; by hand, or generated in a loop:"
          },
          {
            "type": "code",
            "src": "class Proxy:\n    def __init__(self, target):\n        self._target = target\n    def __getattr__(self, name):\n        return getattr(self._target, name)\n\nfor name in (\"__len__\", \"__getitem__\", \"__iter__\", \"__contains__\"):\n    def forward(self, *args, _name=name):\n        return getattr(self._target, _name)(*args)\n    setattr(Proxy, name, forward)\n\np = Proxy([10, 20, 30])\nprint(len(p), p[0], 20 in p, list(p), p.count(10))",
            "label": null,
            "output": "3 10 True [10, 20, 30] 1",
            "isError": false
          },
          {
            "type": "p",
            "html": "Libraries such as <code>wrapt</code> and <code>unittest.mock.MagicMock</code> do the same: <code>MagicMock</code> exists precisely because a plain <code>Mock</code> cannot intercept dunder calls."
          }
        ]
      },
      {
        "q": "Why does <code>+=</code> behave differently on a list stored in a tuple? Explain <code>t = ([1],); t[0] += [2]</code>.",
        "level": "hard",
        "answer": [
          {
            "type": "code",
            "src": "t = ([1],)\ntry:\n    t[0] += [2]\nexcept TypeError as e:\n    print(\"TypeError:\", e)\nprint(t)",
            "label": null,
            "output": "TypeError: 'tuple' object does not support item assignment\n([1, 2],)",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>t[0] += [2]</code> expands to three steps: read <code>x = t[0]</code>; compute <code>x = x.__iadd__([2])</code>; store <code>t[0] = x</code>. <code>list.__iadd__</code> mutates the list in place and returns it, so the append has already happened. Then the store calls <code>tuple.__setitem__</code>, which does not exist, and raises. You get both an exception <em>and</em> a changed value. Using <code>t[0].extend([2])</code> avoids the store step entirely."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: Special method names",
        "url": "https://docs.python.org/3/reference/datamodel.html#special-method-names"
      },
      {
        "label": "Python docs: Emulating numeric types",
        "url": "https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types"
      },
      {
        "label": "Python docs: functools.total_ordering",
        "url": "https://docs.python.org/3/library/functools.html#functools.total_ordering"
      },
      {
        "label": "Python docs: The NotImplemented constant",
        "url": "https://docs.python.org/3/library/constants.html#NotImplemented"
      }
    ]
  },
  {
    "id": "descriptors",
    "title": "Descriptors",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "A descriptor is any object whose class defines <code>__get__</code>, <code>__set__</code> or <code>__delete__</code>, stored as a <em>class</em> attribute. When you access that attribute through an instance, Python calls those methods instead of returning the object itself.",
      "It sounds niche, but it is the machinery behind methods, <code>self</code>, <code>property</code>, <code>classmethod</code>, <code>staticmethod</code>, <code>__slots__</code>, <code>functools.cached_property</code>, and every ORM field you have used. Understanding descriptors is understanding how attribute access actually works."
    ],
    "sections": [
      {
        "title": "The protocol",
        "body": [
          {
            "type": "p",
            "html": "Three optional methods, plus a fourth that tells the descriptor its own name:"
          },
          {
            "type": "table",
            "head": [
              "Method",
              "Called for",
              "Receives"
            ],
            "rows": [
              [
                "<code>__get__(self, obj, objtype)</code>",
                "<code>obj.attr</code> and <code>Class.attr</code>",
                "The instance (or <code>None</code> via the class) and the class"
              ],
              [
                "<code>__set__(self, obj, value)</code>",
                "<code>obj.attr = value</code>",
                "The instance and the new value"
              ],
              [
                "<code>__delete__(self, obj)</code>",
                "<code>del obj.attr</code>",
                "The instance"
              ],
              [
                "<code>__set_name__(self, owner, name)</code>",
                "Once, when the class is created",
                "The owning class and the attribute name"
              ]
            ]
          },
          {
            "type": "code",
            "src": "class Traced:\n    def __set_name__(self, owner, name):\n        self.name = name\n        print(f\"__set_name__: {owner.__name__}.{name}\")\n\n    def __get__(self, obj, objtype=None):\n        print(f\"__get__ obj={type(obj).__name__} objtype={objtype.__name__}\")\n        return 42 if obj is not None else self\n\n    def __set__(self, obj, value):\n        print(f\"__set__ {self.name} = {value!r}\")\n\nclass Account:\n    balance = Traced()\n\nprint(\"--- class created ---\")\nacct = Account()\nprint(acct.balance)\nacct.balance = 100\nprint(Account.balance.__class__.__name__)",
            "label": null,
            "output": "__set_name__: Account.balance\n--- class created ---\n__get__ obj=Account objtype=Account\n42\n__set__ balance = 100\n__get__ obj=NoneType objtype=Account\nTraced",
            "isError": false
          },
          {
            "type": "p",
            "html": "Notice that <code>acct.balance = 100</code> did not create an instance attribute &mdash; the descriptor intercepted the assignment. And accessing through the class passed <code>obj=None</code>; returning <code>self</code> in that case is the convention, so tools can introspect the descriptor."
          }
        ]
      },
      {
        "title": "Data vs non-data descriptors, and the lookup order",
        "body": [
          {
            "type": "p",
            "html": "A descriptor that defines <code>__set__</code> or <code>__delete__</code> is a <strong>data descriptor</strong>. One with only <code>__get__</code> is a <strong>non-data descriptor</strong>. The difference decides who wins when the instance also has an attribute of the same name."
          },
          {
            "type": "code",
            "src": "class Data:\n    def __get__(self, obj, t=None): return \"from data descriptor\"\n    def __set__(self, obj, v): raise AttributeError(\"read-only\")\n\nclass NonData:\n    def __get__(self, obj, t=None): return \"from non-data descriptor\"\n\nclass C:\n    d = Data()\n    n = NonData()\n\nc = C()\nc.__dict__[\"d\"] = \"from instance dict\"    # sneak past __set__\nc.__dict__[\"n\"] = \"from instance dict\"\n\nprint(\"c.d ->\", c.d)\nprint(\"c.n ->\", c.n)",
            "label": null,
            "output": "c.d -> from data descriptor\nc.n -> from instance dict",
            "isError": false
          },
          {
            "type": "p",
            "html": "That gives the full order <code>object.__getattribute__</code> follows for <code>obj.name</code>:"
          },
          {
            "type": "table",
            "head": [
              "Step",
              "Look for",
              "If found"
            ],
            "rows": [
              [
                "1",
                "<code>name</code> in <code>type(obj).__mro__</code>",
                "Remember it; if it is a <strong>data descriptor</strong>, call its <code>__get__</code> and stop"
              ],
              [
                "2",
                "<code>name</code> in <code>obj.__dict__</code>",
                "Return it"
              ],
              [
                "3",
                "The class attribute from step 1",
                "If it is a non-data descriptor call <code>__get__</code>, else return it as is"
              ],
              [
                "4",
                "Nothing found",
                "Call <code>__getattr__</code> if defined, else raise <code>AttributeError</code>"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Data descriptors win over the instance, so <code>property</code> cannot be bypassed by assignment. Non-data descriptors lose to the instance, so a method can be shadowed per instance and a cache can store its result in the instance dict."
          }
        ]
      },
      {
        "title": "Functions are descriptors: how methods and self work",
        "body": [
          {
            "type": "p",
            "html": "There is no special &ldquo;method&rdquo; type in a class body. <code>def</code> inside a class makes a plain function. Functions define <code>__get__</code>, and that is where <code>self</code> comes from: looking the function up through an instance returns a <em>bound method</em> that remembers the instance."
          },
          {
            "type": "code",
            "src": "class Greeter:\n    def hello(self, name):\n        return f\"{type(self).__name__} says hi to {name}\"\n\ng = Greeter()\nraw = Greeter.__dict__[\"hello\"]\n\nprint(type(raw).__name__)                    # a plain function\nprint(type(g.hello).__name__)                # a bound method\nbound = raw.__get__(g, Greeter)              # what g.hello does\nprint(bound(\"ann\"))\nprint(bound.__self__ is g, bound.__func__ is raw)\nprint(Greeter.hello(g, \"bob\"))               # unbound: pass self yourself",
            "label": null,
            "output": "function\nmethod\nGreeter says hi to ann\nTrue True\nGreeter says hi to bob",
            "isError": false
          },
          {
            "type": "p",
            "html": "Every <code>g.hello</code> builds a new bound method object, so <code>g.hello is g.hello</code> is <code>False</code> (CPython avoids actually allocating one for a direct call <code>g.hello()</code>). And because functions are non-data descriptors, an instance attribute with the same name shadows the method."
          }
        ]
      },
      {
        "title": "property is a data descriptor",
        "body": [
          {
            "type": "p",
            "html": "<code>property</code> is not special syntax. It is a class written in C, and you can write an equivalent one in a dozen lines:"
          },
          {
            "type": "code",
            "src": "class MyProperty:\n    def __init__(self, fget=None, fset=None):\n        self.fget, self.fset = fget, fset\n\n    def __get__(self, obj, objtype=None):\n        if obj is None:\n            return self\n        return self.fget(obj)\n\n    def __set__(self, obj, value):\n        if self.fset is None:\n            raise AttributeError(\"can't set attribute\")\n        self.fset(obj, value)\n\n    def setter(self, fset):\n        return type(self)(self.fget, fset)   # a new descriptor, like property\n\nclass Temperature:\n    def __init__(self, celsius):\n        self._c = celsius\n\n    @MyProperty\n    def fahrenheit(self):\n        return self._c * 9 / 5 + 32\n\n    @fahrenheit.setter\n    def fahrenheit(self, f):\n        self._c = (f - 32) * 5 / 9\n\nt = Temperature(100)\nprint(t.fahrenheit)\nt.fahrenheit = 32\nprint(t._c)",
            "label": null,
            "output": "212.0\n0.0",
            "isError": false
          },
          {
            "type": "p",
            "html": "Because <code>@x.setter</code> returns a <em>new</em> property, the setter function must use the same name as the getter &mdash; otherwise the class ends up with two attributes, one of which has no setter."
          }
        ]
      },
      {
        "title": "classmethod and staticmethod",
        "body": [
          {
            "type": "p",
            "html": "Both are non-data descriptors that change what <code>__get__</code> binds:"
          },
          {
            "type": "code",
            "src": "class MyClassMethod:\n    def __init__(self, f): self.f = f\n    def __get__(self, obj, objtype=None):\n        cls = objtype if objtype is not None else type(obj)\n        return self.f.__get__(cls)       # bind to the class, not the instance\n\nclass MyStaticMethod:\n    def __init__(self, f): self.f = f\n    def __get__(self, obj, objtype=None):\n        return self.f                    # no binding at all\n\nclass Pizza:\n    size = \"medium\"\n\n    @MyClassMethod\n    def make(cls, topping):\n        return f\"{cls.__name__}({topping}, {cls.size})\"\n\n    @MyStaticMethod\n    def slices(n):\n        return n * 8\n\nclass Large(Pizza):\n    size = \"large\"\n\nprint(Pizza.make(\"ham\"), Large().make(\"olive\"), Pizza.slices(2))",
            "label": null,
            "output": "Pizza(ham, medium) Large(olive, large) 16",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Decorator",
              "First argument",
              "Typical use"
            ],
            "rows": [
              [
                "none (plain function)",
                "The instance",
                "Behaviour that needs the object&rsquo;s state"
              ],
              [
                "<code>@classmethod</code>",
                "The class it was called on (subclass-aware)",
                "Alternative constructors: <code>datetime.fromtimestamp</code>, <code>dict.fromkeys</code>"
              ],
              [
                "<code>@staticmethod</code>",
                "Nothing",
                "A helper that belongs in the class namespace but needs neither"
              ]
            ]
          }
        ]
      },
      {
        "title": "Reusable validated fields",
        "body": [
          {
            "type": "p",
            "html": "The payoff of writing your own descriptor is reuse. A property validates one attribute on one class; a descriptor class validates any attribute on any class. <code>__set_name__</code> tells each instance of the descriptor which attribute it manages, so it can store the value in the owner instance&rsquo;s own <code>__dict__</code>."
          },
          {
            "type": "code",
            "src": "class Positive:\n    def __set_name__(self, owner, name):\n        self.public = name\n        self.private = \"_\" + name\n\n    def __get__(self, obj, objtype=None):\n        if obj is None:\n            return self\n        return getattr(obj, self.private)\n\n    def __set__(self, obj, value):\n        if not isinstance(value, (int, float)) or value <= 0:\n            raise ValueError(f\"{self.public} must be positive, got {value!r}\")\n        setattr(obj, self.private, value)\n\nclass Order:\n    quantity = Positive()\n    price = Positive()\n    def __init__(self, quantity, price):\n        self.quantity = quantity         # goes through __set__\n        self.price = price\n\na, b = Order(2, 9.5), Order(5, 1.0)\nprint(a.quantity, b.quantity, vars(a))\ntry:\n    Order(0, 3)\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "2 5 {'_quantity': 2, '_price': 9.5}\nValueError: quantity must be positive, got 0",
            "isError": false
          },
          {
            "type": "p",
            "html": "The classic bug is storing the value on the descriptor (<code>self.value = value</code>). There is only one descriptor object per class attribute, shared by every instance:"
          },
          {
            "type": "code",
            "src": "class Broken:\n    def __get__(self, obj, t=None): return self.value\n    def __set__(self, obj, value): self.value = value   # one slot for everyone\n\nclass Order:\n    quantity = Broken()\n\na, b = Order(), Order()\na.quantity = 2\nb.quantity = 99\nprint(a.quantity)",
            "label": "the bug",
            "output": "99",
            "isError": false
          },
          {
            "type": "note",
            "text": "This pattern &mdash; a descriptor per field, storing into the instance &mdash; is how Django model fields, SQLAlchemy columns and attrs validators work."
          }
        ]
      },
      {
        "title": "cached_property, __getattr__ and __slots__",
        "body": [
          {
            "type": "p",
            "html": "<code>functools.cached_property</code> uses the lookup order cleverly. It is a <em>non-data</em> descriptor: on first access its <code>__get__</code> computes the value and writes it into the instance <code>__dict__</code> under the same name. From then on, step 2 of the lookup finds the instance value and the descriptor is never called again."
          },
          {
            "type": "code",
            "src": "from functools import cached_property\n\nclass Dataset:\n    @cached_property\n    def stats(self):\n        print(\"  computing...\")\n        return {\"mean\": 4.2}\n\nd = Dataset()\nprint(d.stats)\nprint(d.stats)                 # served from d.__dict__\nprint(\"stats\" in vars(d))\ndel d.stats                    # invalidate: next access recomputes\nprint(d.stats)",
            "label": null,
            "output": "  computing...\n{'mean': 4.2}\n{'mean': 4.2}\nTrue\n  computing...\n{'mean': 4.2}",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>__getattr__</code> is the fallback at step 4: it runs only when normal lookup fails. <code>__getattribute__</code> replaces the whole algorithm and runs for <em>every</em> access, which is rarely what you want."
          },
          {
            "type": "code",
            "src": "class Lazy:\n    real = \"found normally\"\n    def __getattr__(self, name):\n        return f\"__getattr__ made up {name!r}\"\n\nx = Lazy()\nprint(x.real)\nprint(x.anything)",
            "label": null,
            "output": "found normally\n__getattr__ made up 'anything'",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>__slots__</code> works by creating one data descriptor per slot on the class. The value lives at a fixed offset inside the instance, and there is no <code>__dict__</code> to fall back to:"
          },
          {
            "type": "code",
            "src": "class P:\n    __slots__ = (\"x\", \"y\")\n\nprint(type(P.__dict__[\"x\"]).__name__)\nprint(hasattr(P.__dict__[\"x\"], \"__set__\"))",
            "label": null,
            "output": "member_descriptor\nTrue",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "When would you write a descriptor instead of using <code>property</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "When the same logic applies to several attributes or several classes. A <code>property</code> is one-off: validating ten numeric fields needs ten nearly identical getter/setter pairs. One <code>Positive</code> or <code>Typed(int)</code> descriptor class, used as <code>price = Positive()</code>, removes that duplication, and <code>__set_name__</code> gives each use its own storage name."
          },
          {
            "type": "p",
            "html": "Use <code>property</code> for a single computed or validated attribute &mdash; it is clearer to read. Reach for a descriptor when you catch yourself copying properties, or when building a framework-style API (fields, columns, typed config)."
          }
        ]
      },
      {
        "q": "<code>cached_property</code> has no <code>__set__</code>. How does it cache, and what is the catch?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Because it is a non-data descriptor, the instance <code>__dict__</code> takes priority over it. The first access falls through to the descriptor&rsquo;s <code>__get__</code>, which computes the value and stores it in <code>obj.__dict__[name]</code>. Every later access finds the dict entry first and never reaches the descriptor. Deleting the attribute removes the dict entry and brings the descriptor back into play."
          },
          {
            "type": "p",
            "html": "The catches: it needs an instance <code>__dict__</code>, so it fails on classes with <code>__slots__</code> (unless <code>__dict__</code> is one of the slots); it can be overwritten by plain assignment; and since Python 3.12 it no longer takes a lock, so two threads can both compute the value."
          },
          {
            "type": "code",
            "src": "from functools import cached_property\n\nclass Slotted:\n    __slots__ = (\"x\",)\n    @cached_property\n    def total(self):\n        return 1\n\ntry:\n    Slotted().total\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "TypeError: No '__dict__' attribute on 'Slotted' instance to cache 'total' property.",
            "isError": false
          }
        ]
      },
      {
        "q": "Is <code>obj.method is obj.method</code> true? Why or why not?",
        "level": "hard",
        "answer": [
          {
            "type": "code",
            "src": "class A:\n    def m(self): pass\n\na = A()\nprint(a.m is a.m)\nprint(a.m == a.m)\nprint(A.m is A.m)\nprint(a.m.__func__ is A.m)",
            "label": null,
            "output": "False\nTrue\nTrue\nTrue",
            "isError": false
          },
          {
            "type": "p",
            "html": "Each access to <code>a.m</code> calls <code>function.__get__</code>, which creates a fresh bound method object. The two objects are different, so <code>is</code> is <code>False</code>; bound methods define <code>__eq__</code> as &ldquo;same function and same <code>__self__</code>&rdquo;, so <code>==</code> is <code>True</code>. Accessing through the class returns the underlying function itself, which is the same object each time."
          },
          {
            "type": "p",
            "html": "The practical consequence: registering <code>a.m</code> as a callback and later trying to unregister it with <code>is</code> fails. Compare with <code>==</code>, or keep the bound method you registered."
          }
        ]
      },
      {
        "q": "What is the difference between <code>__getattr__</code> and <code>__getattribute__</code>, and what goes wrong with the latter?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>__getattr__</code> is called only after normal lookup fails. <code>__getattribute__</code> <em>is</em> normal lookup: it is called for every attribute access on the instance, including <code>self.anything</code> inside your own implementation. Accessing <code>self.x</code> inside it recurses forever; you must delegate with <code>super().__getattribute__(name)</code> or <code>object.__getattribute__(self, name)</code>."
          },
          {
            "type": "code",
            "src": "class Audited:\n    def __init__(self):\n        self.log = []\n        self.value = 1\n\n    def __getattribute__(self, name):\n        log = super().__getattribute__(\"log\")     # not self.log!\n        log.append(name)\n        return super().__getattribute__(name)\n\na = Audited()\na.value; a.value\nprint(object.__getattribute__(a, \"log\"))",
            "label": null,
            "output": "['value', 'value']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Remember too that special-method lookup by operators skips both hooks: <code>len(obj)</code> goes to the type and never calls the instance&rsquo;s <code>__getattribute__</code>."
          }
        ]
      },
      {
        "q": "Why does a validating descriptor that stores <code>self.value = value</code> break, and what are the correct places to store per-instance data?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The descriptor is a class attribute, so there is exactly one descriptor object shared by every instance of the owner class. Storing the value on it means every instance shares one value &mdash; the last write wins."
          },
          {
            "type": "p",
            "html": "Correct options: store into the instance&rsquo;s <code>__dict__</code> under a private name learned from <code>__set_name__</code> (the usual choice); store in the instance under the <em>same</em> name as the descriptor, which works for data descriptors because they take priority over the dict; or keep a <code>weakref.WeakKeyDictionary</code> on the descriptor, keyed by instance, for classes that have no <code>__dict__</code>. A plain dict keyed by instance would leak every instance forever."
          }
        ]
      },
      {
        "q": "What happens when you assign to a property that has no setter?",
        "level": "medium",
        "answer": [
          {
            "type": "code",
            "src": "class Circle:\n    def __init__(self, r): self.r = r\n    @property\n    def area(self): return 3.14159 * self.r ** 2\n\nc = Circle(2)\nc.area = 10",
            "label": null,
            "output": "Traceback (most recent call last):\n  File \"descriptors_q5_0.py\", line 7, in <module>\n    c.area = 10\n    ^^^^^^\nAttributeError: property 'area' of 'Circle' object has no setter",
            "isError": true
          },
          {
            "type": "p",
            "html": "<code>property</code> always defines <code>__set__</code> &mdash; even without a setter function &mdash; so it is a data descriptor and wins over the instance dict. Its <code>__set__</code> raises <code>AttributeError</code> when no setter was provided. That is what makes a getter-only property genuinely read-only, rather than something a plain assignment could shadow."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: Descriptor HowTo Guide",
        "url": "https://docs.python.org/3/howto/descriptor.html"
      },
      {
        "label": "Python docs: Implementing descriptors",
        "url": "https://docs.python.org/3/reference/datamodel.html#implementing-descriptors"
      },
      {
        "label": "Python docs: functools.cached_property",
        "url": "https://docs.python.org/3/library/functools.html#functools.cached_property"
      }
    ]
  },
  {
    "id": "metaclasses",
    "title": "Metaclasses",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "An object is created by calling its class. A class is also an object, so it too is created by calling <em>its</em> class &mdash; and the class of a class is called a <strong>metaclass</strong>. By default that is <code>type</code>. Write your own and you control what happens when a class statement runs: you can inspect, change, register or reject the class before anyone uses it.",
      "Metaclasses are powerful and almost always the wrong first tool. Since Python 3.6, <code>__init_subclass__</code>, <code>__set_name__</code> and class decorators cover most of what they were used for. This page explains how they work so you can read framework code, and when you genuinely need one."
    ],
    "sections": [
      {
        "title": "What a class statement really does",
        "body": [
          {
            "type": "p",
            "html": "When Python executes a <code>class</code> statement it runs these steps, in this order:"
          },
          {
            "type": "table",
            "head": [
              "Step",
              "What happens"
            ],
            "rows": [
              [
                "1. Pick the metaclass",
                "Explicit <code>metaclass=</code>, else the most derived metaclass among the bases, else <code>type</code>"
              ],
              [
                "2. Prepare the namespace",
                "<code>ns = Meta.__prepare__(name, bases, **kw)</code> &mdash; a dict by default"
              ],
              [
                "3. Run the body",
                "The class body executes like a function, with <code>ns</code> as its locals"
              ],
              [
                "4. Create the class",
                "<code>cls = Meta(name, bases, ns, **kw)</code>, i.e. <code>Meta.__new__</code> then <code>Meta.__init__</code>"
              ],
              [
                "5. Inside <code>type.__new__</code>",
                "Calls <code>__set_name__</code> on every attribute, then <code>__init_subclass__</code> on the parent"
              ],
              [
                "6. Decorate and bind",
                "Class decorators run bottom-up, then the result is bound to the name"
              ]
            ]
          },
          {
            "type": "p",
            "html": "A metaclass that prints at each hook makes the order visible:"
          },
          {
            "type": "code",
            "src": "class Field:\n    def __set_name__(self, owner, name):\n        print(f\"5. __set_name__ {name}\")\n\nclass Meta(type):\n    @classmethod\n    def __prepare__(mcls, name, bases, **kw):\n        print(f\"2. __prepare__ {name} {kw}\")\n        return {}\n    def __new__(mcls, name, bases, ns, **kw):\n        print(f\"4. Meta.__new__ {name}, body defined {sorted(k for k in ns if not k.startswith('__'))}\")\n        return super().__new__(mcls, name, bases, ns, **kw)   # kw reaches __init_subclass__\n    def __init__(cls, name, bases, ns, **kw):\n        print(f\"7. Meta.__init__ {name}\")\n        super().__init__(name, bases, ns)\n\nclass Base(metaclass=Meta):\n    def __init_subclass__(cls, **kw):\n        print(f\"6. __init_subclass__ {cls.__name__} {kw}\")\n\ndef decorate(cls):\n    print(f\"8. decorator {cls.__name__}\")\n    return cls\n\nprint(\"---\")\n\n@decorate\nclass Model(Base, table=\"users\"):\n    print(\"3. body runs\")\n    id = Field()",
            "label": null,
            "output": "2. __prepare__ Base {}\n4. Meta.__new__ Base, body defined []\n7. Meta.__init__ Base\n---\n2. __prepare__ Model {'table': 'users'}\n3. body runs\n4. Meta.__new__ Model, body defined ['id']\n5. __set_name__ id\n6. __init_subclass__ Model {'table': 'users'}\n7. Meta.__init__ Model\n8. decorator Model",
            "isError": false
          },
          {
            "type": "p",
            "html": "The three lines above the <code>---</code> come from defining <code>Base</code> itself, which also goes through <code>Meta</code>. Below it, <code>Model</code> runs the full sequence &mdash; and the <code>table=&quot;users&quot;</code> keyword from the class line is handed to both <code>__prepare__</code> and <code>__init_subclass__</code>."
          }
        ]
      },
      {
        "title": "Writing a metaclass",
        "body": [
          {
            "type": "p",
            "html": "A metaclass subclasses <code>type</code>. Override <code>__new__</code> to inspect or change the namespace before the class exists, or <code>__init__</code> to work with the finished class. A common real use is enforcing rules at <em>definition</em> time, so mistakes fail at import instead of in production:"
          },
          {
            "type": "code",
            "src": "class InterfaceMeta(type):\n    required = (\"run\", \"name\")\n\n    def __new__(mcls, name, bases, ns):\n        cls = super().__new__(mcls, name, bases, ns)\n        if bases:                           # skip the abstract root\n            missing = [a for a in mcls.required if not hasattr(cls, a)]\n            if missing:\n                raise TypeError(f\"{name} is missing {missing}\")\n        return cls\n\nclass Task(metaclass=InterfaceMeta):\n    pass\n\nclass Backup(Task):\n    name = \"backup\"\n    def run(self): return \"ok\"\n\nprint(Backup().run())\n\ntry:\n    class Broken(Task):\n        name = \"broken\"\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "ok\nTypeError: Broken is missing ['run']",
            "isError": false
          },
          {
            "type": "p",
            "html": "The error happens when <code>Broken</code> is <em>defined</em>, not when someone later calls <code>run</code>. That is the core value metaclasses offer: code that runs once, per class, at class-creation time."
          }
        ]
      },
      {
        "title": "__call__: controlling instance creation",
        "body": [
          {
            "type": "p",
            "html": "<code>Model()</code> is a call on the class object, so it runs <code>type(Model).__call__</code>. The default <code>type.__call__</code> calls <code>__new__</code>, then <code>__init__</code> if <code>__new__</code> returned an instance of the class. Overriding it on a metaclass intercepts every instantiation:"
          },
          {
            "type": "code",
            "src": "class Singleton(type):\n    _instances = {}\n    def __call__(cls, *args, **kwargs):\n        if cls not in cls._instances:\n            print(f\"creating {cls.__name__}\")\n            cls._instances[cls] = super().__call__(*args, **kwargs)\n        return cls._instances[cls]\n\nclass Settings(metaclass=Singleton):\n    def __init__(self, env=\"dev\"):\n        print(f\"__init__ env={env}\")\n        self.env = env\n\na = Settings(\"prod\")\nb = Settings(\"test\")         # __init__ does not run again\nprint(a is b, b.env)",
            "label": null,
            "output": "creating Settings\n__init__ env=prod\nTrue prod",
            "isError": false
          },
          {
            "type": "note",
            "text": "Before writing a singleton, ask whether a module-level instance would do. Modules are imported once and cached, so <code>settings = Settings()</code> in <code>config.py</code> is already a singleton, with no magic."
          }
        ]
      },
      {
        "title": "__prepare__: a custom class namespace",
        "body": [
          {
            "type": "p",
            "html": "<code>__prepare__</code> returns the mapping the class body executes in. Returning something other than a plain dict lets you observe the body as it runs &mdash; for example, catch a method being silently redefined:"
          },
          {
            "type": "code",
            "src": "class NoDuplicates(dict):\n    def __setitem__(self, key, value):\n        if key in self and not key.startswith(\"__\"):\n            raise TypeError(f\"{key!r} defined twice\")\n        super().__setitem__(key, value)\n\nclass StrictMeta(type):\n    @classmethod\n    def __prepare__(mcls, name, bases):\n        return NoDuplicates()\n    def __new__(mcls, name, bases, ns):\n        return super().__new__(mcls, name, bases, dict(ns))\n\ntry:\n    class Handlers(metaclass=StrictMeta):\n        def on_save(self): return \"v1\"\n        def on_load(self): return \"load\"\n        def on_save(self): return \"v2\"     # copy-paste accident\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "TypeError: 'on_save' defined twice",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>enum.Enum</code> uses exactly this trick to reject duplicate member names. Since 3.6, the default class namespace preserves definition order, so the old reason for <code>__prepare__</code> (returning an <code>OrderedDict</code>) is gone."
          }
        ]
      },
      {
        "title": "Lighter alternatives",
        "body": [
          {
            "type": "p",
            "html": "Most things that once needed a metaclass now have simpler tools that compose better, because a class can only have one metaclass:"
          },
          {
            "type": "code",
            "src": "class Plugin:\n    registry = {}\n\n    def __init_subclass__(cls, name=None, **kwargs):\n        super().__init_subclass__(**kwargs)\n        cls.registry[name or cls.__name__.lower()] = cls\n\nclass CsvExporter(Plugin, name=\"csv\"):\n    pass\n\nclass JsonExporter(Plugin):\n    pass\n\nprint(Plugin.registry)",
            "label": "__init_subclass__: a plugin registry with no metaclass",
            "output": "{'csv': <class '__main__.CsvExporter'>, 'jsonexporter': <class '__main__.JsonExporter'>}",
            "isError": false
          },
          {
            "type": "code",
            "src": "def register(registry):\n    def deco(cls):\n        registry[cls.__name__] = cls\n        return cls\n    return deco\n\nCOMMANDS = {}\n\n@register(COMMANDS)\nclass Deploy: ...\n\n@register(COMMANDS)\nclass Rollback: ...\n\nprint(list(COMMANDS))",
            "label": "a class decorator: explicit, one class at a time",
            "output": "['Deploy', 'Rollback']",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Need",
              "Best tool",
              "Why"
            ],
            "rows": [
              [
                "React to subclasses being defined",
                "<code>__init_subclass__</code>",
                "Plain method, inherited, no metaclass conflicts"
              ],
              [
                "Per-attribute setup (knowing the attribute name)",
                "<code>__set_name__</code> on a descriptor",
                "Each field configures itself"
              ],
              [
                "Transform or register one class",
                "Class decorator",
                "Explicit at the use site, easy to read"
              ],
              [
                "Custom class namespace during the body",
                "Metaclass <code>__prepare__</code>",
                "Nothing else runs that early"
              ],
              [
                "Change behaviour of the class object itself (<code>len(Cls)</code>, <code>Cls[x]</code>, iteration over a class)",
                "Metaclass",
                "Special methods are looked up on the type of the class"
              ],
              [
                "Intercept every instantiation",
                "Metaclass <code>__call__</code> (or <code>__new__</code>)",
                "The call on the class goes to the metaclass"
              ]
            ]
          },
          {
            "type": "p",
            "html": "<code>__class_getitem__</code> is another escape hatch: it lets <code>MyClass[int]</code> work without a metaclass, which is how generics like <code>list[int]</code> are implemented."
          }
        ]
      },
      {
        "title": "Metaclass conflicts",
        "body": [
          {
            "type": "p",
            "html": "A class has exactly one metaclass, and it must be a subclass of the metaclass of every base. Mix two bases whose metaclasses are unrelated and Python cannot choose:"
          },
          {
            "type": "code",
            "src": "from abc import ABCMeta\n\nclass MetaA(type): pass\n\nclass Plugin(metaclass=MetaA): pass\nclass Interface(metaclass=ABCMeta): pass\n\ntry:\n    class Both(Plugin, Interface): pass\nexcept TypeError as e:\n    print(\"TypeError:\", e)\n\nclass CombinedMeta(MetaA, ABCMeta): pass      # derive from both\n\nclass Both(Plugin, Interface, metaclass=CombinedMeta): pass\nprint(type(Both).__mro__)",
            "label": null,
            "output": "TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases\n(<class '__main__.CombinedMeta'>, <class '__main__.MetaA'>, <class 'abc.ABCMeta'>, <class 'type'>, <class 'object'>)",
            "isError": false
          },
          {
            "type": "p",
            "html": "This is the practical reason libraries avoid metaclasses: every one you add is a potential conflict for users who combine your classes with someone else&rsquo;s (ABCs, Qt objects, ORMs). A combined metaclass works only if both metaclasses call <code>super()</code> cooperatively."
          }
        ]
      },
      {
        "title": "Where you meet them in the wild",
        "body": [
          {
            "type": "table",
            "head": [
              "Library",
              "Metaclass",
              "What it does at class creation"
            ],
            "rows": [
              [
                "<code>abc</code>",
                "<code>ABCMeta</code>",
                "Collects abstract methods, blocks instantiation until they are implemented, supports <code>register()</code> for virtual subclasses"
              ],
              [
                "<code>enum</code>",
                "<code>EnumType</code>",
                "Turns class attributes into singleton members, forbids duplicates, makes the class iterable and <code>len()</code>-able"
              ],
              [
                "Django",
                "<code>ModelBase</code>",
                "Reads field descriptors, builds <code>_meta</code>, registers the model"
              ],
              [
                "<code>typing</code>",
                "(mostly removed)",
                "Replaced by <code>__class_getitem__</code> and <code>__init_subclass__</code> in 3.7 &mdash; for speed and to stop conflicts"
              ]
            ]
          },
          {
            "type": "code",
            "src": "from enum import Enum\n\nclass Color(Enum):\n    RED = 1\n    GREEN = 2\n\nprint(type(Color).__name__)\nprint(len(Color), [c.name for c in Color])      # len() and iteration on a class\nprint(Color[\"RED\"], Color(2))                   # indexing and calling a class",
            "label": null,
            "output": "EnumType\n2 ['RED', 'GREEN']\nColor.RED Color.GREEN",
            "isError": false
          },
          {
            "type": "p",
            "html": "Every one of those operations &mdash; <code>len</code>, iterating, indexing, calling with a value &mdash; is a special method on <code>EnumType</code>, operating on the class object."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What is a metaclass, and when would you actually use one?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A metaclass is the class of a class: the thing called to create a class object when a <code>class</code> statement runs. <code>type</code> is the default. Custom ones subclass <code>type</code> and override <code>__new__</code>, <code>__init__</code>, <code>__prepare__</code> or <code>__call__</code>."
          },
          {
            "type": "p",
            "html": "Genuine uses today: customising the class namespace (<code>__prepare__</code>), giving class objects their own behaviour (<code>len(Color)</code>, <code>Model.objects</code> as a class-level property), and frameworks that need to process every class in a hierarchy. For registration, validation of subclasses and per-field setup, prefer <code>__init_subclass__</code>, <code>__set_name__</code> or a class decorator. Tim Peters&rsquo; line is still the honest answer: if you are wondering whether you need one, you don&rsquo;t."
          }
        ]
      },
      {
        "q": "Implement a singleton with <code>__new__</code> and with a metaclass. What is different?",
        "level": "hard",
        "answer": [
          {
            "type": "code",
            "src": "class ViaNew:\n    _instance = None\n    def __new__(cls, *args, **kwargs):\n        if cls._instance is None:\n            cls._instance = super().__new__(cls)\n        return cls._instance\n    def __init__(self, value):\n        print(f\"ViaNew.__init__({value})\")\n        self.value = value\n\nclass SingletonMeta(type):\n    def __call__(cls, *args, **kwargs):\n        if \"_instance\" not in cls.__dict__:\n            cls._instance = super().__call__(*args, **kwargs)\n        return cls._instance\n\nclass ViaMeta(metaclass=SingletonMeta):\n    def __init__(self, value):\n        print(f\"ViaMeta.__init__({value})\")\n        self.value = value\n\na, b = ViaNew(1), ViaNew(2)\nprint(\"ViaNew:\", a is b, a.value)\nc, d = ViaMeta(1), ViaMeta(2)\nprint(\"ViaMeta:\", c is d, c.value)",
            "label": null,
            "output": "ViaNew.__init__(1)\nViaNew.__init__(2)\nViaNew: True 2\nViaMeta.__init__(1)\nViaMeta: True 1",
            "isError": false
          },
          {
            "type": "p",
            "html": "With <code>__new__</code>, <code>type.__call__</code> still runs <code>__init__</code> on the returned object every time, so the second call silently overwrites the state. The metaclass version short-circuits <code>__call__</code> itself, so <code>__init__</code> runs once. Checking <code>cls.__dict__</code> rather than <code>hasattr</code> also stops a subclass from inheriting its parent&rsquo;s instance."
          }
        ]
      },
      {
        "q": "In what order do <code>__prepare__</code>, the class body, <code>__new__</code>, <code>__init__</code>, <code>__set_name__</code> and <code>__init_subclass__</code> run?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "<code>__prepare__</code> creates the namespace, the body fills it, then the metaclass is called: <code>Meta.__new__</code> runs and, inside <code>type.__new__</code>, the class object is built, <code>__set_name__</code> is called on every descriptor in the namespace, and then the parent&rsquo;s <code>__init_subclass__</code> runs. Only after <code>__new__</code> returns does <code>Meta.__init__</code> run. Class decorators come last. The trace in the first section above shows it: 2, 3, 4, 5, 6, 7, 8."
          },
          {
            "type": "p",
            "html": "The detail interviewers probe: <code>__init_subclass__</code> runs <em>before</em> <code>Meta.__init__</code>, so a metaclass that sets up attributes in <code>__init__</code> cannot rely on them being there during <code>__init_subclass__</code>. Do that setup in <code>__new__</code> instead."
          }
        ]
      },
      {
        "q": "Build a plugin registry where defining a subclass is enough to register it.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Use <code>__init_subclass__</code> &mdash; no metaclass needed. Accept keyword arguments from the class statement, and always forward the rest to <code>super()</code> so the hook cooperates with other base classes."
          },
          {
            "type": "code",
            "src": "class Handler:\n    handlers = {}\n\n    def __init_subclass__(cls, *, event, **kwargs):\n        super().__init_subclass__(**kwargs)\n        if event in Handler.handlers:\n            raise TypeError(f\"duplicate handler for {event!r}\")\n        Handler.handlers[event] = cls\n\n    @classmethod\n    def dispatch(cls, event, payload):\n        return cls.handlers[event]().handle(payload)\n\nclass OnSignup(Handler, event=\"signup\"):\n    def handle(self, p): return f\"welcome {p}\"\n\nclass OnDelete(Handler, event=\"delete\"):\n    def handle(self, p): return f\"goodbye {p}\"\n\nprint(Handler.dispatch(\"signup\", \"ann\"))\nprint(sorted(Handler.handlers))",
            "label": null,
            "output": "welcome ann\n['delete', 'signup']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Writing <code>Handler.handlers</code> rather than <code>cls.handlers</code> matters: it keeps one shared registry even if a subclass ever defines its own <code>handlers</code> attribute."
          }
        ]
      },
      {
        "q": "Why do you get &ldquo;metaclass conflict&rdquo;, and how do you resolve it?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "A class&rsquo;s metaclass must be a (non-strict) subclass of the metaclasses of all its bases, so that every base&rsquo;s class-level behaviour still applies. If two bases have unrelated metaclasses, no candidate satisfies that and Python raises <code>TypeError</code>."
          },
          {
            "type": "p",
            "html": "Fix it by defining a metaclass that inherits from both and passing it explicitly: <code>class M(MetaA, MetaB): pass</code>, then <code>class C(A, B, metaclass=M)</code>. It only works if both metaclasses use <code>super()</code> in their <code>__new__</code>/<code>__init__</code>. The better long-term fix is removing a metaclass that could have been <code>__init_subclass__</code>."
          }
        ]
      },
      {
        "q": "What does <code>type(name, bases, dict)</code> do, and how is it related to <code>class</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It creates a new class. It is literally step 4 of executing a <code>class</code> statement, with the namespace you pass in place of one produced by running a body. Metaclass <code>__new__</code> methods end by calling <code>super().__new__(mcls, name, bases, ns)</code>, which is this same call."
          },
          {
            "type": "code",
            "src": "def describe(self):\n    return f\"{type(self).__name__}({self.__dict__})\"\n\nRecord = type(\"Record\", (), {\"__repr__\": describe, \"kind\": \"row\"})\nr = Record()\nr.id = 7\nprint(r, Record.kind, type(Record))",
            "label": null,
            "output": "Record({'id': 7}) row <class 'type'>",
            "isError": false
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: Customizing class creation",
        "url": "https://docs.python.org/3/reference/datamodel.html#customizing-class-creation"
      },
      {
        "label": "PEP 487 — Simpler customisation of class creation",
        "url": "https://peps.python.org/pep-0487/"
      },
      {
        "label": "PEP 3115 — Metaclasses in Python 3000",
        "url": "https://peps.python.org/pep-3115/"
      }
    ]
  },
  {
    "id": "mro",
    "title": "Method Resolution Order",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "When you call <code>obj.method()</code> and several classes in the hierarchy define <code>method</code>, Python needs one unambiguous answer to &ldquo;which one?&rdquo;. It gets it by flattening the inheritance graph into a single ordered list &mdash; the <strong>method resolution order</strong> &mdash; and taking the first class in that list that defines the name.",
      "With single inheritance the list is obvious. With multiple inheritance it is computed by the <strong>C3 linearization</strong> algorithm, and it is also what <code>super()</code> walks. Most confusion about <code>super()</code> disappears once you see that it means &ldquo;the next class in the MRO&rdquo;, not &ldquo;my parent&rdquo;."
    ],
    "sections": [
      {
        "title": "The MRO is a list you can read",
        "body": [
          {
            "type": "p",
            "html": "Every class has a <code>__mro__</code> tuple. Attribute lookup walks it left to right and stops at the first class whose <code>__dict__</code> has the name."
          },
          {
            "type": "code",
            "src": "class Animal:\n    def speak(self): return \"...\"\n    def move(self):  return \"moves\"\n\nclass Dog(Animal):\n    def speak(self): return \"woof\"\n\nclass Puppy(Dog):\n    pass\n\nprint([c.__name__ for c in Puppy.__mro__])\np = Puppy()\nprint(p.speak(), p.move())\n\nfor name in (\"speak\", \"move\"):\n    owner = next(c for c in Puppy.__mro__ if name in c.__dict__)\n    print(f\"{name} found on {owner.__name__}\")",
            "label": null,
            "output": "['Puppy', 'Dog', 'Animal', 'object']\nwoof moves\nspeak found on Dog\nmove found on Animal",
            "isError": false
          }
        ]
      },
      {
        "title": "The diamond",
        "body": [
          {
            "type": "p",
            "html": "Multiple inheritance gets interesting when two bases share an ancestor. Should <code>D</code> look in <code>A</code> before or after <code>C</code>?"
          },
          {
            "type": "code",
            "src": "class A:\n    def who(self): return \"A\"\n\nclass B(A):\n    pass\n\nclass C(A):\n    def who(self): return \"C\"\n\nclass D(B, C):\n    pass\n\nprint([k.__name__ for k in D.__mro__])\nprint(D().who())",
            "label": null,
            "output": "['D', 'B', 'C', 'A', 'object']\nC",
            "isError": false
          },
          {
            "type": "p",
            "html": "Python 2&rsquo;s old-style classes used depth-first search, which would have visited <code>D, B, A</code> and returned <code>&quot;A&quot;</code> &mdash; ignoring <code>C</code>&rsquo;s override even though <code>C</code> is a more specific class than <code>A</code>. C3 guarantees a class always comes before its own bases, so <code>A</code> is pushed after both <code>B</code> and <code>C</code>."
          },
          {
            "type": "p",
            "html": "C3 enforces three rules together:"
          },
          {
            "type": "table",
            "head": [
              "Rule",
              "Meaning"
            ],
            "rows": [
              [
                "Children before parents",
                "A class always appears before every one of its bases"
              ],
              [
                "Local order is kept",
                "If a class lists <code>(B, C)</code>, B comes before C in the result"
              ],
              [
                "Monotonic",
                "A class&rsquo;s MRO is consistent with each of its bases&rsquo; MROs &mdash; a subclass never reorders what its parents agreed on"
              ]
            ]
          }
        ]
      },
      {
        "title": "Computing C3 by hand",
        "body": [
          {
            "type": "p",
            "html": "The rule: <em>L[C] = C + merge(L[B1], L[B2], &hellip;, [B1, B2, &hellip;])</em>. To merge, repeatedly take the first head of a list that does not appear in the <em>tail</em> (anything after the first element) of any other list; remove it everywhere and repeat. If no head qualifies, there is no consistent order."
          },
          {
            "type": "code",
            "src": "def c3(cls):\n    if cls is object:\n        return [object]\n    seqs = [c3(b) for b in cls.__bases__] + [list(cls.__bases__)]\n    result = [cls]\n    while any(seqs):\n        for seq in seqs:\n            if not seq:\n                continue\n            head = seq[0]\n            if not any(head in s[1:] for s in seqs):\n                break\n        else:\n            raise TypeError(\"no consistent MRO\")\n        result.append(head)\n        seqs = [[x for x in s if x is not head] for s in seqs]\n    return result\n\nclass A: pass\nclass B(A): pass\nclass C(A): pass\nclass D(B, C): pass\nclass E: pass\nclass F(D, E): pass\n\nprint([k.__name__ for k in c3(F)])\nprint(c3(F) == list(F.__mro__))",
            "label": null,
            "output": "['F', 'D', 'B', 'C', 'A', 'E', 'object']\nTrue",
            "isError": false
          },
          {
            "type": "p",
            "html": "Walking it for <code>D(B, C)</code>: merge <code>[B, A, object]</code>, <code>[C, A, object]</code>, <code>[B, C]</code>. Take <code>B</code> (not in any tail). Now <code>A</code> heads the first list but is in the tail of <code>[C, A, object]</code>, so skip it and take <code>C</code>. Now <code>A</code> is free, then <code>object</code>. Result: <code>D, B, C, A, object</code>."
          }
        ]
      },
      {
        "title": "When no order exists",
        "body": [
          {
            "type": "p",
            "html": "If two bases demand opposite orders, C3 refuses rather than guessing, and the class statement fails:"
          },
          {
            "type": "code",
            "src": "class X: pass\nclass Y: pass\nclass XY(X, Y): pass      # says X before Y\nclass YX(Y, X): pass      # says Y before X\n\ntry:\n    class Z(XY, YX): pass\nexcept TypeError as e:\n    print(\"TypeError:\", e)\n\ntry:\n    class Bad(object, X): pass    # base listed before its subclass\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "TypeError: Cannot create a consistent method resolution order (MRO) for bases X, Y\nTypeError: Cannot create a consistent method resolution order (MRO) for bases object, X",
            "isError": false
          },
          {
            "type": "p",
            "html": "The second case catches a common beginner mistake: listing a general base before a more specific one. Put more specific classes (mixins, subclasses) first and general ones last."
          }
        ]
      },
      {
        "title": "super() means &ldquo;next in the MRO&rdquo;",
        "body": [
          {
            "type": "p",
            "html": "<code>super()</code> does not look at the class&rsquo;s parent. It looks at the MRO of the <em>instance&rsquo;s actual type</em> and continues from the class where the method is defined. In a diamond that means <code>B</code>&rsquo;s <code>super()</code> can call <code>C</code> &mdash; a class <code>B</code> knows nothing about."
          },
          {
            "type": "code",
            "src": "class Base:\n    def save(self):\n        print(\"Base.save\")\n\nclass Timestamped(Base):\n    def save(self):\n        mro = type(self).__mro__\n        print(\"Timestamped.save, next is\", mro[mro.index(Timestamped) + 1].__name__)\n        super().save()\n\nclass Validated(Base):\n    def save(self):\n        print(\"Validated.save\")\n        super().save()\n\nclass Model(Timestamped, Validated):\n    def save(self):\n        print(\"Model.save\")\n        super().save()\n\nprint([c.__name__ for c in Model.__mro__])\nModel().save()\nprint(\"--- same class, alone ---\")\nTimestamped().save()",
            "label": null,
            "output": "['Model', 'Timestamped', 'Validated', 'Base', 'object']\nModel.save\nTimestamped.save, next is Validated\nValidated.save\nBase.save\n--- same class, alone ---\nTimestamped.save, next is Base\nBase.save",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>Timestamped.save</code> calls <code>super().save()</code> both times, but in a <code>Model</code> the next class is <code>Validated</code>, and in a plain <code>Timestamped</code> it is <code>Base</code>. Every method in the chain runs exactly once, and <code>Base.save</code> runs last. This is <strong>cooperative multiple inheritance</strong>: it works only if every class in the chain calls <code>super()</code>."
          }
        ]
      },
      {
        "title": "Cooperative __init__",
        "body": [
          {
            "type": "p",
            "html": "Constructors are where cooperation usually breaks, because each class wants different arguments and does not know who comes next. The pattern: take the keyword arguments you need, pass the rest on with <code>**kwargs</code>, and let the root class receive nothing extra."
          },
          {
            "type": "code",
            "src": "class Shape:\n    def __init__(self, **kwargs):\n        super().__init__(**kwargs)          # object.__init__ takes no args\n\nclass Colored(Shape):\n    def __init__(self, color=\"black\", **kwargs):\n        self.color = color\n        super().__init__(**kwargs)\n\nclass Named(Shape):\n    def __init__(self, name=\"?\", **kwargs):\n        self.name = name\n        super().__init__(**kwargs)\n\nclass Label(Colored, Named):\n    def __init__(self, text, **kwargs):\n        self.text = text\n        super().__init__(**kwargs)\n\nl = Label(\"hi\", color=\"red\", name=\"title\")\nprint(vars(l))\n\ntry:\n    Label(\"hi\", colour=\"red\")               # typo reaches object.__init__\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "{'text': 'hi', 'color': 'red', 'name': 'title'}\nTypeError: object.__init__() takes exactly one argument (the instance to initialize)",
            "isError": false
          },
          {
            "type": "p",
            "html": "The typo check is a feature: an unknown keyword travels all the way up and <code>object.__init__</code> rejects it, so misspelt options fail loudly instead of being silently ignored."
          },
          {
            "type": "note",
            "text": "Use keyword arguments throughout a cooperative hierarchy. Positional arguments cannot be routed safely, because no class knows which position belongs to which class in the final MRO."
          }
        ]
      },
      {
        "title": "Mixins and why order matters",
        "body": [
          {
            "type": "p",
            "html": "A mixin is a small class that adds one behaviour and is meant to be combined with others. Because the MRO is ordered left to right, a mixin listed <em>first</em> wraps the classes after it:"
          },
          {
            "type": "code",
            "src": "class Store:\n    def get(self, key):\n        return f\"value-of-{key}\"\n\nclass LoggingMixin:\n    def get(self, key):\n        result = super().get(key)\n        print(f\"  log: get({key!r}) -> {result!r}\")\n        return result\n\nclass CachingMixin:\n    def get(self, key):\n        cache = self.__dict__.setdefault(\"_cache\", {})\n        if key not in cache:\n            print(f\"  miss: {key!r}\")\n            cache[key] = super().get(key)\n        return cache[key]\n\nclass LogThenCache(LoggingMixin, CachingMixin, Store): pass\nclass CacheThenLog(CachingMixin, LoggingMixin, Store): pass\n\nfor cls in (LogThenCache, CacheThenLog):\n    print(cls.__name__)\n    s = cls()\n    s.get(\"a\"); s.get(\"a\")",
            "label": null,
            "output": "LogThenCache\n  miss: 'a'\n  log: get('a') -> 'value-of-a'\n  log: get('a') -> 'value-of-a'\nCacheThenLog\n  miss: 'a'\n  log: get('a') -> 'value-of-a'",
            "isError": false
          },
          {
            "type": "p",
            "html": "With logging outermost, every call is logged, including cache hits. With caching outermost, hits return before the logger is reached, so only misses are logged. Same classes, different program: the order of bases is part of the design."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What is printed?",
        "level": "medium",
        "answer": [
          {
            "type": "code",
            "src": "class A:\n    def go(self): return [\"A\"]\nclass B(A):\n    def go(self): return [\"B\"] + super().go()\nclass C(A):\n    def go(self): return [\"C\"] + super().go()\nclass D(B, C):\n    def go(self): return [\"D\"] + super().go()\n\nprint(D().go())\nprint(B().go())",
            "label": null,
            "output": "['D', 'B', 'C', 'A']\n['B', 'A']",
            "isError": false
          },
          {
            "type": "p",
            "html": "The MRO of <code>D</code> is <code>D, B, C, A, object</code>. Each <code>super().go()</code> moves one step along <em>that</em> list, so <code>B</code>&rsquo;s super call reaches <code>C</code>, not <code>A</code>. On a plain <code>B</code> instance the MRO is <code>B, A, object</code>, so the same line in <code>B</code> reaches <code>A</code>. Every class runs exactly once, and the shared base <code>A</code> runs once, at the end."
          }
        ]
      },
      {
        "q": "Compute the MRO of <code>Z</code> by hand.",
        "level": "hard",
        "answer": [
          {
            "type": "code",
            "src": "class O: pass\nclass A(O): pass\nclass B(O): pass\nclass C(O): pass\nclass D(O): pass\nclass E(O): pass\nclass K1(A, B, C): pass\nclass K2(D, B, E): pass\nclass K3(D, A): pass\nclass Z(K1, K2, K3): pass\n\nprint(\" \".join(k.__name__ for k in Z.__mro__))",
            "label": "the classic example from the C3 paper",
            "output": "Z K1 K2 K3 D A B C E O object",
            "isError": false
          },
          {
            "type": "p",
            "html": "Start with <code>merge([K1 A B C O], [K2 D B E O], [K3 D A O], [K1 K2 K3])</code> and always scan heads from the first list:"
          },
          {
            "type": "p",
            "html": "<code>K1</code> is in no tail &rarr; take it.<br><code>A</code> is in the tail of <code>[K3 D A O]</code> &rarr; blocked; <code>K2</code> is free &rarr; take it.<br><code>A</code> still blocked; <code>D</code> is in the tail of <code>[K3 D A O]</code> &rarr; blocked; <code>K3</code> is free &rarr; take it.<br><code>A</code> is in the tail of <code>[D A O]</code> &rarr; blocked; <code>D</code> is now free &rarr; take it.<br>Now <code>A</code> is free, then <code>B</code>, <code>C</code>, <code>E</code>, and finally <code>O</code>."
          },
          {
            "type": "p",
            "html": "Result: <code>Z K1 K2 K3 D A B C E O</code>. Notice <code>D</code> jumps ahead of <code>A</code> even though <code>K1</code> (listed first) inherits from <code>A</code>: <code>K3</code> said <code>D</code> before <code>A</code>, and C3 keeps every local order."
          }
        ]
      },
      {
        "q": "Why does Python refuse to create this class?",
        "level": "hard",
        "answer": [
          {
            "type": "code",
            "src": "class Base: pass\nclass Mixin(Base): pass\n\nclass Widget(Base, Mixin): pass",
            "label": null,
            "output": "Traceback (most recent call last):\n  File \"mro_q2_0.py\", line 4, in <module>\n    class Widget(Base, Mixin): pass\nTypeError: Cannot create a consistent method resolution order (MRO) for bases Base, Mixin",
            "isError": true
          },
          {
            "type": "p",
            "html": "<code>Widget(Base, Mixin)</code> asks for <code>Base</code> before <code>Mixin</code> (local order). But <code>Mixin</code> is a subclass of <code>Base</code>, so it must come before <code>Base</code> (children before parents). Both rules cannot hold, so there is no linearization. Swap the bases &mdash; <code>class Widget(Mixin, Base)</code> &mdash; or drop <code>Base</code> altogether since <code>Mixin</code> already brings it in."
          }
        ]
      },
      {
        "q": "What is the difference between calling <code>Parent.__init__(self)</code> and <code>super().__init__()</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>Parent.__init__(self)</code> hard-codes one class; <code>super()</code> follows the MRO. In a diamond, explicit calls run the shared base once per path:"
          },
          {
            "type": "code",
            "src": "class Root:\n    def __init__(self): print(\"Root.__init__\")\n\nclass Left(Root):\n    def __init__(self): print(\"Left\"); Root.__init__(self)\nclass Right(Root):\n    def __init__(self): print(\"Right\"); Root.__init__(self)\nclass Both(Left, Right):\n    def __init__(self):\n        Left.__init__(self)\n        Right.__init__(self)\n\nBoth()",
            "label": "explicit calls: Root runs twice",
            "output": "Left\nRoot.__init__\nRight\nRoot.__init__",
            "isError": false
          },
          {
            "type": "code",
            "src": "class Root:\n    def __init__(self): print(\"Root.__init__\")\n\nclass Left(Root):\n    def __init__(self): print(\"Left\"); super().__init__()\nclass Right(Root):\n    def __init__(self): print(\"Right\"); super().__init__()\nclass Both(Left, Right):\n    def __init__(self): super().__init__()\n\nBoth()",
            "label": "super(): each class once",
            "output": "Left\nRight\nRoot.__init__",
            "isError": false
          },
          {
            "type": "p",
            "html": "Running <code>Root.__init__</code> twice can reset state, open two connections, or register a handler twice. Mixing the two styles is the worst case: one explicit call anywhere in the chain breaks it for every class after it."
          }
        ]
      },
      {
        "q": "How does zero-argument <code>super()</code> know which class and instance to use?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The compiler sees <code>super</code> (or <code>__class__</code>) used inside a function defined in a class body, and gives that function an implicit closure cell called <code>__class__</code>, filled in with the class once it is created. At run time, <code>super()</code> reads that cell for the class, and the first argument of the current frame for the instance. It is exactly <code>super(__class__, self)</code>."
          },
          {
            "type": "code",
            "src": "class A:\n    def f(self):\n        return super()\n    def g(self):\n        return __class__\n\nprint(A.f.__code__.co_freevars)\nprint(A().g())\n\ndef outside(self):\n    return super().__repr__()\n\nclass B:\n    method = outside\n\ntry:\n    B().method()\nexcept RuntimeError as e:\n    print(\"RuntimeError:\", e)",
            "label": null,
            "output": "('__class__',)\n<class '__main__.A'>\nRuntimeError: super(): __class__ cell not found",
            "isError": false
          },
          {
            "type": "p",
            "html": "So zero-argument <code>super()</code> fails in a function defined outside the class body and attached later, and it binds to the class where the method was <em>written</em> &mdash; which is exactly what makes the MRO walk correct in subclasses."
          }
        ]
      },
      {
        "q": "Your mixin&rsquo;s method never runs. What is the most likely reason?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Either the mixin is listed <em>after</em> the base class that defines the same method (so the base is found first and the mixin is never reached), or a class earlier in the MRO overrides the method without calling <code>super()</code>, which ends the chain. Print <code>Cls.__mro__</code> to check the order."
          },
          {
            "type": "code",
            "src": "class Base:\n    def run(self): return \"base\"\n\nclass AuditMixin:\n    def run(self): return \"audited \" + super().run()\n\nclass Wrong(Base, AuditMixin): pass\nclass Right(AuditMixin, Base): pass\n\nprint(Wrong().run(), \"|\", Right().run())",
            "label": null,
            "output": "base | audited base",
            "isError": false
          },
          {
            "type": "p",
            "html": "Convention: mixins on the left, the concrete base class on the right, and every overriding method calls <code>super()</code>."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "The Python 2.3 Method Resolution Order (C3)",
        "url": "https://docs.python.org/3/howto/mro.html"
      },
      {
        "label": "Python docs: super()",
        "url": "https://docs.python.org/3/library/functions.html#super"
      },
      {
        "label": "Raymond Hettinger — Python’s super() considered super!",
        "url": "https://rhettinger.wordpress.com/2011/05/26/super-considered-super/"
      }
    ]
  },
  {
    "id": "slots-dataclasses-typing",
    "title": "__slots__, Dataclasses and Typing",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "Three features that change how you write classes. <code>__slots__</code> trades the per-instance <code>__dict__</code> for fixed storage: less memory, faster attribute access, no accidental attributes. <code>dataclasses</code> generate <code>__init__</code>, <code>__repr__</code>, <code>__eq__</code> and more from type-annotated fields. And type hints document and check all of it &mdash; without Python enforcing any of it at run time.",
      "Each is simple on its own. The interview questions live in the interactions: slots with inheritance, mutable defaults in dataclasses, frozen dataclasses and hashing, and what annotations really are at run time."
    ],
    "sections": [
      {
        "title": "__slots__: no per-instance dict",
        "body": [
          {
            "type": "p",
            "html": "Normally every instance carries a <code>__dict__</code>, a hash table for its attributes. Declaring <code>__slots__</code> tells the class to reserve a fixed array of slots instead. Each slot becomes a descriptor on the class that reads and writes a fixed offset in the object."
          },
          {
            "type": "code",
            "src": "import sys, tracemalloc\n\nclass PointDict:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n\nclass PointSlots:\n    __slots__ = (\"x\", \"y\")\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n\ndef measure(cls, n=100_000):\n    tracemalloc.start()\n    objs = [cls(i, i) for i in range(n)]\n    size = tracemalloc.get_traced_memory()[0]\n    tracemalloc.stop()\n    return size // n\n\nprint(\"bytes per instance, dict :\", measure(PointDict))\nprint(\"bytes per instance, slots:\", measure(PointSlots))\nprint(hasattr(PointSlots(1, 2), \"__dict__\"), type(PointSlots.__dict__[\"x\"]).__name__)",
            "label": null,
            "output": "bytes per instance, dict : 127\nbytes per instance, slots: 87\nFalse member_descriptor",
            "isError": false
          },
          {
            "type": "p",
            "html": "Slots also make the attribute set closed, which turns typos into errors instead of silently creating new attributes:"
          },
          {
            "type": "code",
            "src": "class Account:\n    __slots__ = (\"owner\", \"balance\")\n    def __init__(self, owner):\n        self.owner, self.balance = owner, 0\n\na = Account(\"ann\")\ntry:\n    a.balanse = 100                   # typo\nexcept AttributeError as e:\n    print(\"AttributeError:\", e)",
            "label": null,
            "output": "AttributeError: 'Account' object has no attribute 'balanse' and no __dict__ for setting new attributes",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "Since CPython 3.11 a plain instance stores its attributes in a compact inline array and only creates a real <code>__dict__</code> when needed, so the saving from <code>__slots__</code> is smaller than older articles claim. It is still real, as the measurement shows, and it matters when you hold millions of small objects."
          }
        ]
      },
      {
        "title": "Slots and inheritance",
        "body": [
          {
            "type": "p",
            "html": "Slots only take effect if <em>every</em> class in the hierarchy uses them. A subclass that does not declare <code>__slots__</code> gets a <code>__dict__</code> again, and you lose both the memory saving and the closed attribute set. Each subclass should declare only its <em>new</em> slots; repeating a parent's slot wastes space and shadows it."
          },
          {
            "type": "code",
            "src": "class Base:\n    __slots__ = (\"id\",)\n\nclass Leaky(Base):                   # forgot __slots__\n    pass\n\nclass Tight(Base):\n    __slots__ = (\"name\",)            # only the new attribute\n\nl, t = Leaky(), Tight()\nl.anything = 1                       # works: Leaky has a __dict__ again\nprint(hasattr(l, \"__dict__\"), hasattr(t, \"__dict__\"))\ntry:\n    t.anything = 1\nexcept AttributeError as e:\n    print(\"AttributeError:\", e)",
            "label": null,
            "output": "True False\nAttributeError: 'Tight' object has no attribute 'anything' and no __dict__ for setting new attributes",
            "isError": false
          },
          {
            "type": "p",
            "html": "Other consequences to know: instances cannot be weakly referenced unless <code>\"__weakref__\"</code> is a slot; slots and a class attribute with the same name conflict (so slot defaults must be set in <code>__init__</code>); and multiple inheritance from two classes that both have non-empty slots fails with a layout conflict."
          },
          {
            "type": "code",
            "src": "import weakref\n\nclass A:\n    __slots__ = (\"x\",)\nclass B:\n    __slots__ = (\"y\",)\n\ntry:\n    weakref.ref(A())\nexcept TypeError as e:\n    print(\"TypeError:\", e)\n\ntry:\n    class AB(A, B): pass\nexcept TypeError as e:\n    print(\"TypeError:\", e)\n\ntry:\n    class Defaults:\n        __slots__ = (\"x\",)\n        x = 0                        # class attribute clashes with the slot\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "TypeError: cannot create weak reference to 'A' object\nTypeError: multiple bases have instance lay-out conflict\nValueError: 'x' in __slots__ conflicts with class variable",
            "isError": false
          }
        ]
      },
      {
        "title": "Dataclasses: what gets generated",
        "body": [
          {
            "type": "p",
            "html": "<code>@dataclass</code> reads the class's annotated fields and writes the boilerplate methods for you. It is an ordinary class afterwards &mdash; no base class, no metaclass, no run-time cost per instance beyond what you would have written by hand."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass, field, fields, asdict, replace\n\n@dataclass\nclass Item:\n    name: str\n    price: float\n    qty: int = 1\n    tags: list[str] = field(default_factory=list)\n\na = Item(\"pen\", 1.5)\nb = Item(\"pen\", 1.5)\nprint(a)                                # __repr__\nprint(a == b, a is b)                   # __eq__ compares fields as a tuple\nprint([f.name for f in fields(Item)])\nprint(asdict(replace(a, qty=3)))        # copy with changes, then to dict\nprint(Item.__hash__)                    # eq=True and not frozen -> unhashable",
            "label": null,
            "output": "Item(name='pen', price=1.5, qty=1, tags=[])\nTrue False\n['name', 'price', 'qty', 'tags']\n{'name': 'pen', 'price': 1.5, 'qty': 3, 'tags': []}\nNone",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Option",
              "Generates / does",
              "Default"
            ],
            "rows": [
              [
                "<code>init</code>",
                "<code>__init__</code> from the fields",
                "True"
              ],
              [
                "<code>repr</code>",
                "<code>__repr__</code>",
                "True"
              ],
              [
                "<code>eq</code>",
                "<code>__eq__</code> (fields compared as a tuple, same class only)",
                "True"
              ],
              [
                "<code>order</code>",
                "<code>__lt__</code>, <code>__le__</code>, <code>__gt__</code>, <code>__ge__</code>",
                "False"
              ],
              [
                "<code>frozen</code>",
                "Assignment raises <code>FrozenInstanceError</code>; with <code>eq</code>, also <code>__hash__</code>",
                "False"
              ],
              [
                "<code>slots</code>",
                "Builds a new class with <code>__slots__</code> (3.10+)",
                "False"
              ],
              [
                "<code>kw_only</code>",
                "All fields keyword-only in <code>__init__</code> (3.10+)",
                "False"
              ]
            ]
          }
        ]
      },
      {
        "title": "Mutable defaults and field()",
        "body": [
          {
            "type": "p",
            "html": "A default value is evaluated once, when the class body runs, and shared by every instance &mdash; the same trap as a mutable default argument. Dataclasses refuse the obvious cases (<code>list</code>, <code>dict</code>, <code>set</code>) outright. Use <code>field(default_factory=...)</code> so each instance gets its own."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass, field\n\ntry:\n    @dataclass\n    class Cart:\n        items: list = []\nexcept ValueError as e:\n    print(\"ValueError:\", e)\n\n@dataclass\nclass Cart:\n    items: list = field(default_factory=list)\n    id: int = field(default=0, repr=False, compare=False)\n\nc1, c2 = Cart(), Cart()\nc1.items.append(\"apple\")\nprint(c1, c2, c1.items is c2.items)\nprint(Cart([\"x\"], id=1) == Cart([\"x\"], id=2))   # id excluded from __eq__",
            "label": null,
            "output": "ValueError: mutable default <class 'list'> for field items is not allowed: use default_factory\nCart(items=['apple']) Cart(items=[]) False\nTrue",
            "isError": false
          },
          {
            "type": "p",
            "html": "The check only knows about unhashable built-ins. A mutable default of your own class, or a <code>tuple</code> containing a list, is not caught, so do not rely on it."
          }
        ]
      },
      {
        "title": "__post_init__, InitVar and frozen dataclasses",
        "body": [
          {
            "type": "p",
            "html": "<code>__post_init__</code> runs at the end of the generated <code>__init__</code>, for validation and derived fields. <code>InitVar</code> declares an <code>__init__</code> parameter that is passed to <code>__post_init__</code> but not stored. <code>field(init=False)</code> is a stored field that <code>__init__</code> does not take."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass, field, InitVar\n\n@dataclass\nclass User:\n    email: str\n    password: InitVar[str]               # used once, never stored\n    password_hash: str = field(init=False, repr=False)\n    domain: str = field(init=False)\n\n    def __post_init__(self, password):\n        if \"@\" not in self.email:\n            raise ValueError(f\"bad email {self.email!r}\")\n        self.password_hash = f\"hash({len(password)} chars)\"\n        self.domain = self.email.split(\"@\")[1]\n\nu = User(\"ann@example.com\", \"s3cret\")\nprint(u, \"|\", u.password_hash, \"|\", hasattr(u, \"password\"))\ntry:\n    User(\"nope\", \"x\")\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "User(email='ann@example.com', domain='example.com') | hash(6 chars) | False\nValueError: bad email 'nope'",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>frozen=True</code> makes assignment raise, and together with <code>eq=True</code> generates a <code>__hash__</code> from the fields, so instances work as dict keys and set members. Inside <code>__post_init__</code> of a frozen class you need <code>object.__setattr__</code> to set derived fields."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass, field, FrozenInstanceError\n\n@dataclass(frozen=True, order=True)\nclass Version:\n    major: int\n    minor: int\n    label: str = field(default=\"\", compare=False)\n    key: str = field(init=False, compare=False, repr=False)\n\n    def __post_init__(self):\n        object.__setattr__(self, \"key\", f\"{self.major}.{self.minor}\")\n\nv = Version(1, 2, \"beta\")\nprint(sorted({Version(2, 0), v, Version(1, 2)}), v.key)   # label is not compared, so v == Version(1, 2)\ntry:\n    v.major = 9\nexcept FrozenInstanceError as e:\n    print(\"FrozenInstanceError:\", e)",
            "label": null,
            "output": "[Version(major=1, minor=2, label='beta'), Version(major=2, minor=0, label='')] 1.2\nFrozenInstanceError: cannot assign to field 'major'",
            "isError": false
          },
          {
            "type": "note",
            "text": "Frozen means the fields cannot be rebound, not that the objects they point at are immutable. A frozen dataclass holding a <code>list</code> can still have that list mutated &mdash; and then hashing it fails because lists are unhashable."
          }
        ]
      },
      {
        "title": "Choosing a record type",
        "body": [
          {
            "type": "p",
            "html": "Python has several ways to declare a bundle of named fields. They differ in mutability, memory, and whether they are a class or just a type hint over a dict."
          },
          {
            "type": "code",
            "src": "from collections import namedtuple\nfrom dataclasses import dataclass\nfrom typing import NamedTuple, TypedDict\n\nclass P1(NamedTuple):\n    x: int\n    y: int\n\n@dataclass\nclass P2:\n    x: int\n    y: int\n\n@dataclass(slots=True, frozen=True)\nclass P3:\n    x: int\n    y: int\n\nclass P4(TypedDict):\n    x: int\n    y: int\n\nfor obj in (P1(1, 2), P2(1, 2), P3(1, 2), P4(x=1, y=2)):\n    print(f\"{type(obj).__name__:5} has __dict__={hasattr(obj, '__dict__')!s:5} repr={obj!r}\")\n\nx, y = P1(1, 2)                        # NamedTuple unpacks like a tuple\nprint(P1(1, 2) == (1, 2), P2(1, 2) == (1, 2))",
            "label": null,
            "output": "P1    has __dict__=False repr=P1(x=1, y=2)\nP2    has __dict__=True  repr=P2(x=1, y=2)\nP3    has __dict__=False repr=P3(x=1, y=2)\ndict  has __dict__=False repr={'x': 1, 'y': 2}\nTrue False",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "",
              "NamedTuple",
              "@dataclass",
              "@dataclass(slots, frozen)",
              "TypedDict"
            ],
            "rows": [
              [
                "Mutable",
                "No",
                "Yes",
                "No",
                "Yes (it is a dict)"
              ],
              [
                "Is a tuple / indexable",
                "Yes",
                "No",
                "No",
                "No"
              ],
              [
                "Equal to a plain tuple",
                "Yes",
                "No",
                "No",
                "Equal to a plain dict"
              ],
              [
                "Hashable",
                "Yes",
                "No (default)",
                "Yes",
                "No"
              ],
              [
                "Methods, validation",
                "Methods only",
                "Yes, <code>__post_init__</code>",
                "Yes",
                "No"
              ],
              [
                "Best for",
                "Small immutable records, tuple APIs",
                "General data classes",
                "Many small value objects",
                "Typing JSON-shaped dicts"
              ]
            ]
          }
        ]
      },
      {
        "title": "Type hints are not enforced",
        "body": [
          {
            "type": "p",
            "html": "Annotations are metadata. The interpreter stores them and otherwise ignores them: a function annotated <code>-&gt; int</code> may return a string, and a dataclass field annotated <code>int</code> accepts anything. Checking happens in a separate tool (mypy, pyright) before the code runs, or in libraries that choose to read the annotations at run time (pydantic, FastAPI, dataclasses for field discovery)."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\ndef add(a: int, b: int) -> int:\n    return a + b\n\n@dataclass\nclass Box:\n    size: int\n\nprint(add(\"not \", \"checked\"))\nprint(Box(size=\"large\"))\nprint(add.__annotations__)",
            "label": null,
            "output": "not checked\nBox(size='large')\n{'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}",
            "isError": false
          },
          {
            "type": "p",
            "html": "Python 3.14 evaluates annotations <em>lazily</em> (PEP 649): they are compiled into a function that runs only when someone asks for <code>__annotations__</code>. Forward references to classes defined later no longer need quotes, and an annotation that names something undefined only fails when it is actually inspected."
          },
          {
            "type": "code",
            "src": "import annotationlib\n\nclass Node:\n    def link(self, other: Node) -> Tree:     # Tree does not exist yet\n        return other\n\nprint(\"class created fine\")\nann = annotationlib.get_annotations(Node.link, format=annotationlib.Format.FORWARDREF)\nprint(ann)\n\nclass Tree: pass\nprint(Node.link.__annotations__)              # evaluated now that Tree exists",
            "label": null,
            "output": "class created fine\n{'other': <class '__main__.Node'>, 'return': ForwardRef('Tree', owner=<function Node.link at 0x...>)}\n{'other': <class '__main__.Node'>, 'return': <class '__main__.Tree'>}",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "Before 3.14, annotations were evaluated when the <code>def</code> or <code>class</code> ran, so <code>other: Node</code> inside <code>Node</code> was a <code>NameError</code>; code wrote <code>\"Node\"</code> in quotes or used <code>from __future__ import annotations</code>, which turns every annotation into a string."
          }
        ]
      },
      {
        "title": "Generics, Protocols and the typing toolbox",
        "body": [
          {
            "type": "p",
            "html": "Generics let a hint say what a container holds. Python 3.12 added a compact syntax for type parameters: <code>def first[T](xs: list[T]) -&gt; T</code> declares <code>T</code> right on the function, replacing <code>T = TypeVar(\"T\")</code>."
          },
          {
            "type": "code",
            "src": "from collections.abc import Callable, Iterable\n\ndef first[T](items: Iterable[T], default: T) -> T:\n    for x in items:\n        return x\n    return default\n\nclass Stack[T]:\n    def __init__(self) -> None:\n        self._items: list[T] = []\n    def push(self, item: T) -> None:\n        self._items.append(item)\n    def pop(self) -> T:\n        return self._items.pop()\n\ntype Handler = Callable[[str], None]          # 3.12 type alias statement\n\ns = Stack[int]()\ns.push(3)\nprint(first([], 0), first(\"abc\", \"?\"), s.pop())\nprint(Stack.__type_params__, Handler.__value__)",
            "label": null,
            "output": "0 a 3\n(T,) collections.abc.Callable[[str], None]",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>Protocols</strong> give static <em>duck typing</em>: any class with the right methods matches, with no inheritance. <code>@runtime_checkable</code> also lets <code>isinstance</code> check them &mdash; but only for the presence of the methods, not their signatures."
          },
          {
            "type": "code",
            "src": "from typing import Protocol, runtime_checkable\n\n@runtime_checkable\nclass SupportsClose(Protocol):\n    def close(self) -> None: ...\n\nclass File:\n    def close(self) -> None:\n        print(\"  file closed\")\n\nclass Socket:\n    def close(self, how):               # different signature!\n        print(\"  socket closed\", how)\n\ndef shutdown(resources: list[SupportsClose]) -> None:\n    for r in resources:\n        r.close()\n\nshutdown([File()])\nprint(isinstance(File(), SupportsClose), isinstance(Socket(), SupportsClose),\n      isinstance(\"text\", SupportsClose))",
            "label": null,
            "output": "  file closed\nTrue True False",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Hint",
              "Means"
            ],
            "rows": [
              [
                "<code>X | None</code> (was <code>Optional[X]</code>)",
                "X or None"
              ],
              [
                "<code>A | B</code> (was <code>Union[A, B]</code>)",
                "either type"
              ],
              [
                "<code>Literal[\"r\", \"w\"]</code>",
                "only these exact values"
              ],
              [
                "<code>Final</code>",
                "must not be reassigned"
              ],
              [
                "<code>Callable[[int, str], bool]</code>",
                "a function taking int, str and returning bool"
              ],
              [
                "<code>Self</code>",
                "the type of the current class (for fluent methods)"
              ],
              [
                "<code>Any</code> vs <code>object</code>",
                "<code>Any</code> turns checking off; <code>object</code> accepts anything but allows almost nothing"
              ],
              [
                "<code>TYPE_CHECKING</code>",
                "True only for the type checker: imports used just for hints"
              ]
            ]
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "When would you use <code>__slots__</code>, and what do you give up?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Use it for classes with many instances and a fixed set of attributes &mdash; nodes, points, records parsed from a large file &mdash; where the per-instance memory and slightly faster attribute access matter, or where you want misspelled attributes to raise. You give up dynamic attributes, the <code>__dict__</code> (so <code>vars(obj)</code> fails), weak references unless you add <code>__weakref__</code>, class-level defaults for slot names, and easy multiple inheritance. Every class in the hierarchy must declare slots or the benefit disappears."
          },
          {
            "type": "p",
            "html": "<code>@dataclass(slots=True)</code> is the low-effort way to get them: it builds the slotted class for you from the fields."
          }
        ]
      },
      {
        "q": "Why does this dataclass raise an error, and what would happen with a plain class?",
        "level": "medium",
        "answer": [
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\nclass Plain:\n    def __init__(self, tags=[]):\n        self.tags = tags\n\na, b = Plain(), Plain()\na.tags.append(\"shared!\")\nprint(b.tags)\n\ntry:\n    @dataclass\n    class D:\n        tags: list = []\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "['shared!']\nValueError: mutable default <class 'list'> for field tags is not allowed: use default_factory",
            "isError": false
          },
          {
            "type": "p",
            "html": "Defaults are evaluated once, when the <code>def</code> or <code>class</code> runs, and that one object is shared by every call or instance. The plain class silently shares the list. <code>dataclass</code> detects a <code>list</code>, <code>dict</code> or <code>set</code> default and refuses, pointing you to <code>field(default_factory=list)</code>, which calls the factory once per instance."
          }
        ]
      },
      {
        "q": "A frozen dataclass is used as a dict key. A teammate removes <code>frozen=True</code> to allow updates and keys stop working. Why?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "With <code>eq=True</code> (the default), dataclass sets <code>__hash__ = None</code> unless the class is frozen, because a mutable object whose fields can change must not be hashable &mdash; its hash would change while it sat in a dict. Removing <code>frozen</code> therefore makes instances unhashable, and every dict or set that used them fails."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Key:\n    a: int\n\n@dataclass\nclass MutableKey:\n    a: int\n\nprint(hash(Key(1)) == hash(Key(1)), MutableKey.__hash__)\ntry:\n    {MutableKey(1): \"x\"}\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "True None\nTypeError: cannot use 'MutableKey' as a dict key (unhashable type: 'MutableKey')",
            "isError": false
          },
          {
            "type": "p",
            "html": "If updates are needed, keep the key frozen and build new values with <code>dataclasses.replace(key, a=2)</code>. Forcing <code>unsafe_hash=True</code> on a mutable class brings back the lost-in-the-wrong-bucket bug."
          }
        ]
      },
      {
        "q": "Python ignores type hints at run time. So how do FastAPI and pydantic validate request data from them?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Annotations are stored as data on the function or class (<code>__annotations__</code>), and any code can read them. Those libraries call <code>typing.get_type_hints</code> (or <code>annotationlib</code> on 3.14), walk the resulting types, and build validators and converters &mdash; the interpreter itself still checks nothing."
          },
          {
            "type": "code",
            "src": "import typing\n\ndef validate(func, **kwargs):\n    hints = typing.get_type_hints(func)\n    for name, value in kwargs.items():\n        expected = hints[name]\n        if not isinstance(value, expected):\n            try:\n                kwargs[name] = expected(value)        # coerce, like pydantic\n            except (TypeError, ValueError):\n                raise TypeError(f\"{name}: expected {expected.__name__}, got {value!r}\")\n    return func(**kwargs)\n\ndef create_user(name: str, age: int) -> str:\n    return f\"{name} ({age})\"\n\nprint(validate(create_user, name=\"ann\", age=\"34\"))\ntry:\n    validate(create_user, name=\"bob\", age=\"old\")\nexcept TypeError as e:\n    print(\"TypeError:\", e)",
            "label": null,
            "output": "ann (34)\nTypeError: age: expected int, got 'old'",
            "isError": false
          }
        ]
      },
      {
        "q": "What is the difference between a <code>Protocol</code> and an abstract base class?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "An ABC is <em>nominal</em>: a class matches only if it inherits from the ABC (or is registered). A Protocol is <em>structural</em>: any class with matching methods matches, without knowing the Protocol exists. That makes Protocols the right tool for describing what a function needs from third-party objects you cannot change. ABCs can also provide shared method implementations and refuse to instantiate subclasses that miss abstract methods; Protocols are mainly for the type checker, and their <code>isinstance</code> support (with <code>@runtime_checkable</code>) checks only that the method names exist."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: __slots__",
        "url": "https://docs.python.org/3/reference/datamodel.html#slots"
      },
      {
        "label": "Python docs: dataclasses",
        "url": "https://docs.python.org/3/library/dataclasses.html"
      },
      {
        "label": "Python docs: typing",
        "url": "https://docs.python.org/3/library/typing.html"
      },
      {
        "label": "PEP 649: Deferred evaluation of annotations",
        "url": "https://peps.python.org/pep-0649/"
      },
      {
        "label": "PEP 695: Type parameter syntax",
        "url": "https://peps.python.org/pep-0695/"
      },
      {
        "label": "PEP 544: Protocols",
        "url": "https://peps.python.org/pep-0544/"
      }
    ]
  },
  {
    "id": "decorators",
    "title": "Decorators",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "<code>@decorator</code> above a <code>def</code> is one line of syntax sugar: <code>func = decorator(func)</code>. That is all the language does. What makes decorators powerful is everything that single call can do &mdash; wrap the function, replace it, register it, attach data to it, or turn it into a completely different kind of object such as a <code>property</code>.",
      "This page goes from the rebinding rule to closures, <code>functools.wraps</code>, decorators with arguments, stacking order, class-based decorators and the descriptor bug they hit on methods, class decorators, and the standard-library decorators worth knowing cold."
    ],
    "sections": [
      {
        "title": "The one rule: decoration is rebinding, at definition time",
        "body": [
          {
            "type": "p",
            "html": "A decorator is any callable that takes the object being defined and returns something. The name is then bound to whatever it returned. It runs <em>once</em>, when the <code>def</code> executes &mdash; usually at import &mdash; not on every call."
          },
          {
            "type": "code",
            "src": "def announce(func):\n    print(f\"decorating {func.__name__}\")\n    return func\n\n@announce\ndef greet():\n    return \"hi\"\n\n# exactly the same as:\ndef wave():\n    return \"o/\"\nwave = announce(wave)\n\nprint(\"--- now calling ---\")\nprint(greet(), wave())",
            "label": null,
            "output": "decorating greet\ndecorating wave\n--- now calling ---\nhi o/",
            "isError": false
          },
          {
            "type": "p",
            "html": "Because the result replaces the name, a decorator can return something that is not a function at all:"
          },
          {
            "type": "code",
            "src": "def run_now(func):\n    return func()\n\n@run_now\ndef config():\n    return {\"debug\": True}\n\nprint(config)            # the name now holds the return value",
            "label": null,
            "output": "{'debug': True}",
            "isError": false
          }
        ]
      },
      {
        "title": "Wrapping: closures and functools.wraps",
        "body": [
          {
            "type": "p",
            "html": "Most decorators return a new function that calls the original. The wrapper reaches the original through a closure, and accepts <code>*args, **kwargs</code> so it fits any signature."
          },
          {
            "type": "code",
            "src": "import functools, time\n\ndef timed(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.perf_counter()\n        try:\n            return func(*args, **kwargs)\n        finally:\n            elapsed = time.perf_counter() - start\n            print(f\"{func.__name__} took under 1s: {elapsed < 1}\")\n    return wrapper\n\n@timed\ndef add(a, b):\n    \"\"\"Add two numbers.\"\"\"\n    return a + b\n\nprint(add(2, 3))\nprint(add.__name__, \"|\", add.__doc__, \"|\", add.__wrapped__)",
            "label": null,
            "output": "add took under 1s: True\n5\nadd | Add two numbers. | <function add at 0x...>",
            "isError": false
          },
          {
            "type": "p",
            "html": "Without <code>functools.wraps</code> the decorated function would report the wrapper&rsquo;s name and docstring. That breaks logs, <code>help()</code>, test runners, web frameworks that route by function name, and pickling. <code>wraps</code> copies <code>__name__</code>, <code>__qualname__</code>, <code>__doc__</code>, <code>__module__</code>, <code>__dict__</code> and annotations, and sets <code>__wrapped__</code> so <code>inspect.signature</code> shows the real parameters."
          },
          {
            "type": "code",
            "src": "import functools, inspect\n\ndef bare(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper\n\ndef wrapped(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper\n\ndef area(width: float, height: float = 1.0) -> float:\n    return width * height\n\nfor deco in (bare, wrapped):\n    f = deco(area)\n    print(f\"{deco.__name__:8} name={f.__name__:8} signature={inspect.signature(f)}\")",
            "label": "what tools see, with and without wraps",
            "output": "bare     name=wrapper  signature=(*args, **kwargs)\nwrapped  name=area     signature=(width: float, height: float = 1.0) -> float",
            "isError": false
          },
          {
            "type": "note",
            "text": "Put <code>@functools.wraps(func)</code> on every wrapper you write. There is no situation where leaving it off is better."
          }
        ]
      },
      {
        "title": "Decorators that take arguments",
        "body": [
          {
            "type": "p",
            "html": "<code>@retry(times=3)</code> first <em>calls</em> <code>retry(times=3)</code>, and the result of that call is the decorator. So a configurable decorator is three nested functions: the factory taking the options, the decorator taking the function, and the wrapper taking the call&rsquo;s arguments."
          },
          {
            "type": "code",
            "src": "import functools\n\ndef retry(times=3, exceptions=(Exception,)):\n    def decorator(func):\n        @functools.wraps(func)\n        def wrapper(*args, **kwargs):\n            for attempt in range(1, times + 1):\n                try:\n                    return func(*args, **kwargs)\n                except exceptions as e:\n                    print(f\"  attempt {attempt} failed: {e}\")\n                    if attempt == times:\n                        raise\n        return wrapper\n    return decorator\n\ncalls = {\"n\": 0}\n\n@retry(times=4, exceptions=(ConnectionError,))\ndef flaky():\n    calls[\"n\"] += 1\n    if calls[\"n\"] < 3:\n        raise ConnectionError(\"timeout\")\n    return \"connected\"\n\nprint(flaky())",
            "label": null,
            "output": "  attempt 1 failed: timeout\n  attempt 2 failed: timeout\nconnected",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Layer",
              "Called when",
              "Receives",
              "Returns"
            ],
            "rows": [
              [
                "<code>retry(...)</code>",
                "The <code>@</code> line is evaluated",
                "Options",
                "The decorator"
              ],
              [
                "<code>decorator(func)</code>",
                "Right after, at definition time",
                "The function",
                "The wrapper"
              ],
              [
                "<code>wrapper(*args)</code>",
                "Every call",
                "The call&rsquo;s arguments",
                "The result"
              ]
            ]
          }
        ]
      },
      {
        "title": "Stacking order",
        "body": [
          {
            "type": "p",
            "html": "Stacked decorators are applied bottom-up &mdash; the one closest to <code>def</code> wraps first &mdash; so the top one ends up outermost and runs first on each call."
          },
          {
            "type": "code",
            "src": "import functools\n\ndef tag(name):\n    def decorator(func):\n        print(f\"applying {name}\")\n        @functools.wraps(func)\n        def wrapper(*a, **k):\n            print(f\"  enter {name}\")\n            result = func(*a, **k)\n            print(f\"  exit  {name}\")\n            return result\n        return wrapper\n    return decorator\n\n@tag(\"outer\")\n@tag(\"inner\")\ndef work():\n    print(\"  work\")\n\nprint(\"--- call ---\")\nwork()",
            "label": null,
            "output": "applying inner\napplying outer\n--- call ---\n  enter outer\n  enter inner\n  work\n  exit  inner\n  exit  outer",
            "isError": false
          },
          {
            "type": "p",
            "html": "This matters in real code. <code>@app.route</code> must be on top so the framework registers the fully decorated function; <code>@login_required</code> placed <em>above</em> the route decorator would never run, because the router already holds a reference to the undecorated inner function. Similarly <code>@classmethod</code> and <code>@staticmethod</code> go on top of other decorators, since they produce descriptors rather than plain functions."
          }
        ]
      },
      {
        "title": "Stateful decorators: function attributes and classes",
        "body": [
          {
            "type": "p",
            "html": "A decorator often needs state that survives between calls &mdash; a counter, a cache, a rate-limit window. Either keep it in the closure and expose it as an attribute of the wrapper, or write the decorator as a class with <code>__call__</code>."
          },
          {
            "type": "code",
            "src": "import functools\n\ndef count_calls(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        wrapper.calls += 1\n        return func(*args, **kwargs)\n    wrapper.calls = 0\n    return wrapper\n\nclass CountCalls:\n    def __init__(self, func):\n        functools.update_wrapper(self, func)\n        self.func = func\n        self.calls = 0\n    def __call__(self, *args, **kwargs):\n        self.calls += 1\n        return self.func(*args, **kwargs)\n\n@count_calls\ndef ping(): return \"pong\"\n\n@CountCalls\ndef pong(): return \"ping\"\n\nping(); ping(); pong()\nprint(ping.calls, pong.calls, pong.__name__)",
            "label": null,
            "output": "2 1 pong",
            "isError": false
          },
          {
            "type": "p",
            "html": "The class-based version reads well but hides a trap: put it on a <em>method</em> and <code>self</code> goes missing."
          },
          {
            "type": "code",
            "src": "import functools\n\nclass CountCalls:\n    def __init__(self, func):\n        functools.update_wrapper(self, func)\n        self.func, self.calls = func, 0\n    def __call__(self, *args, **kwargs):\n        self.calls += 1\n        return self.func(*args, **kwargs)\n\nclass Service:\n    @CountCalls\n    def status(self):\n        return \"up\"\n\nService().status()",
            "label": "the bug",
            "output": "Traceback (most recent call last):\n  File \"decorators_s4_3.py\", line 16, in <module>\n    Service().status()\n    ~~~~~~~~~~~~~~~~^^\n  File \"decorators_s4_3.py\", line 9, in __call__\n    return self.func(*args, **kwargs)\n           ~~~~~~~~~^^^^^^^^^^^^^^^^^\nTypeError: Service.status() missing 1 required positional argument: 'self'",
            "isError": true
          },
          {
            "type": "p",
            "html": "Functions become methods because they are descriptors (<code>__get__</code> binds <code>self</code>). An instance of <code>CountCalls</code> is not, so <code>Service().status</code> returns the <code>CountCalls</code> object unbound and <code>self</code> is never passed. Adding <code>__get__</code> fixes it:"
          },
          {
            "type": "code",
            "src": "import functools, types\n\nclass CountCalls:\n    def __init__(self, func):\n        functools.update_wrapper(self, func)\n        self.func, self.calls = func, 0\n    def __call__(self, *args, **kwargs):\n        self.calls += 1\n        return self.func(*args, **kwargs)\n    def __get__(self, obj, objtype=None):\n        if obj is None:\n            return self\n        return types.MethodType(self, obj)      # bind like a function would\n\nclass Service:\n    @CountCalls\n    def status(self):\n        return \"up\"\n\ns = Service()\nprint(s.status(), s.status(), Service.status.calls)",
            "label": "the fix",
            "output": "up up 2",
            "isError": false
          }
        ]
      },
      {
        "title": "Class decorators",
        "body": [
          {
            "type": "p",
            "html": "A decorator on a <code>class</code> receives the finished class. It can add methods, register the class, or check it &mdash; a lighter alternative to a metaclass that affects only the class it is written on."
          },
          {
            "type": "code",
            "src": "def auto_repr(cls):\n    fields = list(cls.__init__.__code__.co_varnames[1:cls.__init__.__code__.co_argcount])\n    def __repr__(self):\n        args = \", \".join(f\"{f}={getattr(self, f)!r}\" for f in fields)\n        return f\"{cls.__name__}({args})\"\n    cls.__repr__ = __repr__\n    return cls\n\n@auto_repr\nclass User:\n    def __init__(self, name, age):\n        self.name, self.age = name, age\n\nprint(User(\"ann\", 31))",
            "label": null,
            "output": "User(name='ann', age=31)",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>@dataclass</code> is the famous one: it reads the class&rsquo;s annotations and generates <code>__init__</code>, <code>__repr__</code> and <code>__eq__</code> (and more, on request). <code>@functools.total_ordering</code> fills in the missing comparison methods from <code>__eq__</code> plus one of <code>__lt__</code>/<code>__gt__</code>."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass, field\nfrom functools import total_ordering\n\n@dataclass(order=True)\nclass Version:\n    major: int\n    minor: int = 0\n    tags: list = field(default_factory=list, compare=False)\n\nprint(Version(1, 2), Version(1, 2) < Version(1, 10))\n\n@total_ordering\nclass Money:\n    def __init__(self, cents): self.cents = cents\n    def __eq__(self, o): return self.cents == o.cents\n    def __lt__(self, o): return self.cents < o.cents\n\nprint(Money(5) >= Money(3), Money(5) <= Money(3))",
            "label": null,
            "output": "Version(major=1, minor=2, tags=[]) True\nTrue False",
            "isError": false
          }
        ]
      },
      {
        "title": "Standard-library decorators worth knowing",
        "body": [
          {
            "type": "table",
            "head": [
              "Decorator",
              "What it does",
              "Watch out for"
            ],
            "rows": [
              [
                "<code>@functools.cache</code> / <code>@lru_cache(maxsize=n)</code>",
                "Memoizes by arguments",
                "Arguments must be hashable; on methods it keeps every <code>self</code> alive"
              ],
              [
                "<code>@functools.cached_property</code>",
                "Compute once per instance, store on the instance",
                "Needs <code>__dict__</code>; not thread-locked since 3.12"
              ],
              [
                "<code>@functools.singledispatch</code>",
                "Overload a function on its first argument&rsquo;s type",
                "Dispatches on the first argument only; use <code>singledispatchmethod</code> in classes"
              ],
              [
                "<code>@contextlib.contextmanager</code>",
                "Turn a generator into a <code>with</code>-able object",
                "Wrap the <code>yield</code> in <code>try/finally</code>"
              ],
              [
                "<code>@property</code>, <code>@classmethod</code>, <code>@staticmethod</code>",
                "Build descriptors",
                "Keep them outermost when stacking"
              ],
              [
                "<code>@typing.override</code>, <code>@typing.final</code>",
                "Mark intent for type checkers (3.12+ for <code>override</code>)",
                "No run-time effect beyond setting an attribute"
              ]
            ]
          },
          {
            "type": "code",
            "src": "from functools import cache, singledispatch\n\n@cache\ndef fib(n):\n    return n if n < 2 else fib(n - 1) + fib(n - 2)\n\nprint(fib(80), fib.cache_info().hits)\n\n@singledispatch\ndef describe(x):\n    return f\"something: {x!r}\"\n\n@describe.register\ndef _(x: int):\n    return f\"an int, doubled {x * 2}\"\n\n@describe.register\ndef _(x: list):\n    return f\"a list of {len(x)}\"\n\nprint(describe(21), \"|\", describe([1, 2]), \"|\", describe(2.5))",
            "label": null,
            "output": "23416728348467685 78\nan int, doubled 42 | a list of 2 | something: 2.5",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Write a decorator that works both as <code>@log</code> and as <code>@log(level=&quot;debug&quot;)</code>.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The two forms call the decorator differently: bare <code>@log</code> passes the function as the first positional argument; <code>@log(...)</code> passes only keywords and expects a decorator back. Make the function the optional first positional parameter and the options keyword-only, then branch on whether it was given."
          },
          {
            "type": "code",
            "src": "import functools\n\ndef log(func=None, *, level=\"info\"):\n    if func is None:                       # called as @log(...)\n        return functools.partial(log, level=level)\n\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        print(f\"[{level}] {func.__name__}{args}\")\n        return func(*args, **kwargs)\n    return wrapper\n\n@log\ndef a(x): return x\n\n@log(level=\"debug\")\ndef b(x): return x\n\na(1); b(2)",
            "label": null,
            "output": "[info] a(1,)\n[debug] b(2,)",
            "isError": false
          },
          {
            "type": "p",
            "html": "The keyword-only <code>*</code> is what makes it safe: without it, <code>@log(&quot;debug&quot;)</code> would pass a string as <code>func</code> and try to wrap it."
          }
        ]
      },
      {
        "q": "What does <code>functools.wraps</code> do, and what breaks without it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It copies the wrapped function&rsquo;s metadata &mdash; <code>__name__</code>, <code>__qualname__</code>, <code>__doc__</code>, <code>__module__</code>, <code>__annotations__</code>, and <code>__dict__</code> &mdash; onto the wrapper, and sets <code>wrapper.__wrapped__ = func</code>."
          },
          {
            "type": "p",
            "html": "Without it: every decorated function is called <code>wrapper</code> in tracebacks and logs; <code>help()</code> shows no docstring; <code>inspect.signature</code> shows <code>(*args, **kwargs)</code>, which breaks frameworks that inspect parameters (FastAPI, pytest fixtures, Click); two decorated view functions can collide in a router that keys on <code>__name__</code>; and <code>pickle</code> cannot find the function by name. <code>__wrapped__</code> also lets you reach the original, e.g. to test it without the decorator."
          }
        ]
      },
      {
        "q": "What does this print, and in what order?",
        "level": "medium",
        "answer": [
          {
            "type": "code",
            "src": "def a(f):\n    print(\"a applied\")\n    return lambda: \"a(\" + f() + \")\"\n\ndef b(f):\n    print(\"b applied\")\n    return lambda: \"b(\" + f() + \")\"\n\n@a\n@b\ndef core():\n    return \"core\"\n\nprint(core())",
            "label": null,
            "output": "b applied\na applied\na(b(core))",
            "isError": false
          },
          {
            "type": "p",
            "html": "Decorators apply bottom-up at definition time, so <code>b</code> runs first, then <code>a</code> wraps <code>b</code>&rsquo;s result: <code>core = a(b(core))</code>. At call time the outermost wrapper runs first, which is why <code>a</code>&rsquo;s text is on the outside."
          }
        ]
      },
      {
        "q": "Implement <code>@rate_limit(calls, per_seconds)</code> that raises if called too often.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Keep a sliding window of recent call times in the closure. A <code>deque</code> makes dropping old timestamps cheap. Taking the clock as a parameter makes it testable without sleeping."
          },
          {
            "type": "code",
            "src": "import functools, time\nfrom collections import deque\n\nclass RateLimited(Exception):\n    pass\n\ndef rate_limit(calls, per_seconds, clock=time.monotonic):\n    def decorator(func):\n        recent = deque()\n        @functools.wraps(func)\n        def wrapper(*args, **kwargs):\n            now = clock()\n            while recent and now - recent[0] >= per_seconds:\n                recent.popleft()\n            if len(recent) >= calls:\n                raise RateLimited(f\"{func.__name__}: max {calls} per {per_seconds}s\")\n            recent.append(now)\n            return func(*args, **kwargs)\n        return wrapper\n    return decorator\n\nfake_now = [0.0]\n\n@rate_limit(2, per_seconds=10, clock=lambda: fake_now[0])\ndef send(msg): return f\"sent {msg}\"\n\nprint(send(\"a\"), send(\"b\"))\ntry:\n    send(\"c\")\nexcept RateLimited as e:\n    print(\"RateLimited:\", e)\nfake_now[0] = 10.5\nprint(send(\"d\"))",
            "label": null,
            "output": "sent a sent b\nRateLimited: send: max 2 per 10s\nsent d",
            "isError": false
          },
          {
            "type": "p",
            "html": "Follow-ups to expect: make it thread-safe (guard the deque with a <code>threading.Lock</code>), make it per-user (a dict of deques keyed by an argument), or make it block instead of raise (sleep until <code>recent[0] + per_seconds</code>)."
          }
        ]
      },
      {
        "q": "Why does a class-based decorator break when applied to a method, and how do you fix it?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Methods get <code>self</code> because functions are descriptors: accessing a function through an instance calls <code>function.__get__</code>, which returns a bound method. When a decorator replaces the function with an instance of a class that has <code>__call__</code> but no <code>__get__</code>, attribute access returns that object unchanged, so the call arrives without <code>self</code> and fails with a missing-argument <code>TypeError</code>."
          },
          {
            "type": "p",
            "html": "The fix is to implement <code>__get__</code> and return <code>types.MethodType(self, obj)</code> (or <code>functools.partial(self.__call__, obj)</code>). The simpler alternative is to write the decorator as a function returning a closure, which is a real function and binds automatically."
          }
        ]
      },
      {
        "q": "<code>@lru_cache</code> raises <code>TypeError: unhashable type: 'list'</code>. Why, and what are your options?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>lru_cache</code> builds a dict key from the call&rsquo;s arguments, so every argument must be hashable. A list is mutable &mdash; if it could be a key, mutating it after caching would silently return a stale result."
          },
          {
            "type": "code",
            "src": "from functools import lru_cache\n\n@lru_cache\ndef total(values):\n    return sum(values)\n\nprint(total((1, 2, 3)))          # tuple: fine\ntry:\n    total([1, 2, 3])\nexcept TypeError as e:\n    print(\"TypeError:\", e)\nprint(total.cache_info())",
            "label": null,
            "output": "6\nTypeError: unhashable type: 'list'\nCacheInfo(hits=0, misses=1, maxsize=128, currsize=1)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Options: have callers pass tuples or frozensets; add a thin wrapper that converts <code>tuple(values)</code> before calling the cached function; or key the cache on something that identifies the data (an ID or version number) rather than the data itself."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "PEP 318 — Decorators for functions and methods",
        "url": "https://peps.python.org/pep-0318/"
      },
      {
        "label": "PEP 3129 — Class decorators",
        "url": "https://peps.python.org/pep-3129/"
      },
      {
        "label": "Python docs: functools",
        "url": "https://docs.python.org/3/library/functools.html"
      }
    ]
  },
  {
    "id": "generators",
    "title": "Generators and Iterators",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "Every <code>for</code> loop in Python runs on two small methods: <code>__iter__</code> and <code>__next__</code>. Lists, dicts, files, ranges, database cursors and <code>zip</code> objects all speak this one protocol, and that is why they all work in the same loops, comprehensions and built-ins.",
      "A <strong>generator</strong> is the easiest way to implement the protocol: a function that can pause at <code>yield</code> and resume later with its local variables intact. That single feature gives you lazy pipelines that use constant memory, infinite sequences, two-way coroutines and, historically, the whole foundation <code>async</code>/<code>await</code> was built on."
    ],
    "sections": [
      {
        "title": "The iterator protocol",
        "body": [
          {
            "type": "p",
            "html": "An <strong>iterable</strong> is anything with <code>__iter__</code> that returns an iterator. An <strong>iterator</strong> has <code>__next__</code>, which returns the next value or raises <code>StopIteration</code> when there are none left. A <code>for</code> loop is just those two calls plus a <code>try</code>:"
          },
          {
            "type": "code",
            "src": "nums = [10, 20, 30]\n\n# what `for x in nums: print(x)` actually does\nit = iter(nums)                 # nums.__iter__()\nwhile True:\n    try:\n        x = next(it)            # it.__next__()\n    except StopIteration:\n        break\n    print(x)\n\nprint(type(nums).__name__, \"->\", type(it).__name__)\nprint(iter(it) is it)           # an iterator is its own iterator",
            "label": null,
            "output": "10\n20\n30\nlist -> list_iterator\nTrue",
            "isError": false
          },
          {
            "type": "p",
            "html": "The same protocol is behind unpacking, <code>in</code>, <code>sum</code>, <code>sorted</code>, <code>list()</code>, <code>dict()</code>, <code>zip</code>, <code>enumerate</code>, <code>str.join</code> and <code>yield from</code>. Implement it once and your object works with all of them."
          },
          {
            "type": "table",
            "head": [
              "",
              "Iterable",
              "Iterator"
            ],
            "rows": [
              [
                "Has",
                "<code>__iter__</code> returning a <em>new</em> iterator",
                "<code>__next__</code>, and <code>__iter__</code> returning <code>self</code>"
              ],
              [
                "Examples",
                "<code>list</code>, <code>dict</code>, <code>str</code>, <code>range</code>",
                "<code>iter([...])</code>, files, generators, <code>map</code>, <code>zip</code>"
              ],
              [
                "Loop twice?",
                "Yes, each loop gets a fresh iterator",
                "No, the second loop sees nothing"
              ],
              [
                "Supports <code>len()</code> / indexing?",
                "Often",
                "Almost never"
              ]
            ]
          }
        ]
      },
      {
        "title": "Iterators are single use",
        "body": [
          {
            "type": "p",
            "html": "Because an iterator is its own iterator, a second loop over it continues where the first one stopped &mdash; usually at the end. This bites when a function receives a <code>map</code>, <code>zip</code>, file or generator and iterates it twice."
          },
          {
            "type": "code",
            "src": "squares = map(lambda x: x * x, [1, 2, 3, 4])\nprint(sum(squares))      # consumes everything\nprint(sum(squares))      # nothing left\nprint(list(squares))\n\ndef mean(values):\n    return sum(values) / len(list(values))\n\ntry:\n    print(mean(x for x in [2, 4, 6]))\nexcept ZeroDivisionError as e:\n    print(\"ZeroDivisionError:\", e)   # len saw an exhausted generator",
            "label": null,
            "output": "30\n0\n[]\nZeroDivisionError: division by zero",
            "isError": false
          },
          {
            "type": "p",
            "html": "The second <code>list(values)</code> inside <code>mean</code> found nothing, so the length was 0. Two fixes: materialise once (<code>values = list(values)</code>), or write the function to make a single pass."
          },
          {
            "type": "code",
            "src": "def mean(values):\n    total = count = 0\n    for v in values:             # one pass, works for any iterable\n        total += v\n        count += 1\n    return total / count\n\nprint(mean(x for x in [2, 4, 6]), mean([1, 2]), mean(range(101)))",
            "label": null,
            "output": "4.0 1.5 50.0",
            "isError": false
          },
          {
            "type": "note",
            "text": "If a function needs two passes, either accept a <code>Sequence</code> and say so, or call <code>list()</code> on the argument first. Never assume an iterable can be replayed."
          }
        ]
      },
      {
        "title": "Generator functions: pause and resume",
        "body": [
          {
            "type": "p",
            "html": "Any function containing <code>yield</code> is a generator function. Calling it runs <em>none</em> of its body: it returns a generator object. Each <code>next()</code> runs the body until the next <code>yield</code>, hands that value out, and freezes the frame &mdash; locals, the instruction pointer, any open <code>try</code> blocks &mdash; until the next call."
          },
          {
            "type": "code",
            "src": "import inspect\n\ndef countdown(n):\n    print(\"  started\")\n    while n > 0:\n        print(f\"  yielding {n}\")\n        yield n\n        n -= 1\n    print(\"  finished\")\n\ngen = countdown(2)\nprint(\"created:\", inspect.getgeneratorstate(gen))\nprint(\"got\", next(gen))\nprint(\"state:\", inspect.getgeneratorstate(gen))\nprint(\"got\", next(gen))\ntry:\n    next(gen)\nexcept StopIteration:\n    print(\"StopIteration\")\nprint(\"state:\", inspect.getgeneratorstate(gen))",
            "label": null,
            "output": "created: GEN_CREATED\n  started\n  yielding 2\ngot 2\nstate: GEN_SUSPENDED\n  yielding 1\ngot 1\n  finished\nStopIteration\nstate: GEN_CLOSED",
            "isError": false
          },
          {
            "type": "p",
            "html": "Nothing was printed until the first <code>next()</code>. That laziness is the point: work happens only when a value is asked for, and only as much as is asked for."
          },
          {
            "type": "p",
            "html": "A <code>return value</code> inside a generator ends it, and the value travels on the <code>StopIteration</code> exception as <code>.value</code>. Loops ignore it; <code>yield from</code> (below) picks it up."
          }
        ]
      },
      {
        "title": "Laziness: constant memory and infinite sequences",
        "body": [
          {
            "type": "p",
            "html": "A list comprehension builds every element up front. A generator expression &mdash; same syntax in parentheses &mdash; produces them one at a time. The memory difference is the whole list versus one frame:"
          },
          {
            "type": "code",
            "src": "import sys\n\nas_list = [x * x for x in range(1_000_000)]\nas_gen = (x * x for x in range(1_000_000))\n\nprint(f\"list: {sys.getsizeof(as_list):>10,} bytes (just the pointer array)\")\nprint(f\"gen:  {sys.getsizeof(as_gen):>10,} bytes\")\nprint(sum(as_gen) == sum(as_list))",
            "label": null,
            "output": "list:  8,448,728 bytes (just the pointer array)\ngen:         208 bytes\nTrue",
            "isError": false
          },
          {
            "type": "p",
            "html": "Because nothing is computed ahead of time, a generator can be infinite. You take what you need with <code>itertools.islice</code> or stop on a condition:"
          },
          {
            "type": "code",
            "src": "from itertools import islice, count, takewhile\n\ndef fibonacci():\n    a, b = 0, 1\n    while True:                 # never ends: fine, it is lazy\n        yield a\n        a, b = b, a + b\n\nprint(list(islice(fibonacci(), 10)))\nprint(list(takewhile(lambda x: x < 100, fibonacci())))\nprint(next(n for n in count(1) if n * n > 500))",
            "label": null,
            "output": "[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]\n[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]\n23",
            "isError": false
          },
          {
            "type": "p",
            "html": "Chaining generators gives a <strong>pipeline</strong>: each stage pulls one item from the previous stage, so only one item is in flight at a time no matter how big the input is. This is how you process a 50 GB log file in a few kilobytes of memory."
          },
          {
            "type": "code",
            "src": "lines = [\n    \"INFO start\", \"ERROR disk full\", \"INFO retry\",\n    \"ERROR disk full\", \"ERROR timeout\", \"INFO done\",\n]\n\ndef read(source):\n    for line in source:\n        print(f\"  read  {line!r}\")\n        yield line\n\nerrors = (l for l in read(lines) if l.startswith(\"ERROR\"))\nmessages = (l.split(\" \", 1)[1] for l in errors)\n\nfirst_two = [next(messages), next(messages)]\nprint(first_two)               # stopped reading after the 4th line",
            "label": null,
            "output": "  read  'INFO start'\n  read  'ERROR disk full'\n  read  'INFO retry'\n  read  'ERROR disk full'\n['disk full', 'disk full']",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "<code>sys.getsizeof</code> on a list counts only its array of pointers, not the int objects it points at. The real difference here is larger than the number shown."
          }
        ]
      },
      {
        "title": "Two-way generators: send, throw, close",
        "body": [
          {
            "type": "p",
            "html": "<code>yield</code> is an expression. <code>gen.send(value)</code> resumes the generator and makes the paused <code>yield</code> evaluate to <code>value</code>. The first resume must be <code>next(gen)</code> (or <code>send(None)</code>) to run up to the first <code>yield</code> &mdash; this is called <em>priming</em>."
          },
          {
            "type": "code",
            "src": "def running_average():\n    total = count = 0\n    average = None\n    while True:\n        value = yield average      # hand out average, receive value\n        total += value\n        count += 1\n        average = total / count\n\navg = running_average()\nnext(avg)                          # prime: run to the first yield\nfor v in (10, 20, 60):\n    print(f\"sent {v:>2} -> average {avg.send(v)}\")",
            "label": null,
            "output": "sent 10 -> average 10.0\nsent 20 -> average 15.0\nsent 60 -> average 30.0",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>gen.throw(exc)</code> raises an exception <em>at the paused yield</em>, so the generator can handle it. <code>gen.close()</code> throws <code>GeneratorExit</code>, which runs <code>finally</code> blocks &mdash; generators clean up after themselves."
          },
          {
            "type": "code",
            "src": "def worker():\n    try:\n        while True:\n            try:\n                job = yield\n                print(f\"  processing {job}\")\n            except ValueError as e:\n                print(f\"  recovered from: {e}\")\n    finally:\n        print(\"  cleanup ran\")\n\nw = worker(); next(w)\nw.send(\"job-1\")\nw.throw(ValueError(\"bad input\"))   # handled inside, generator lives on\nw.send(\"job-2\")\nw.close()                          # GeneratorExit -> finally\nprint(\"closed:\", w.gi_frame is None)",
            "label": null,
            "output": "  processing job-1\n  recovered from: bad input\n  processing job-2\n  cleanup ran\nclosed: True",
            "isError": false
          },
          {
            "type": "note",
            "text": "This is how coroutines worked before <code>async def</code>: a scheduler sent results into paused generators. <code>await</code> is built on the same machinery &mdash; see the async internals topic."
          }
        ]
      },
      {
        "title": "yield from: delegating to a sub-generator",
        "body": [
          {
            "type": "p",
            "html": "<code>yield from sub</code> passes every value of <code>sub</code> straight through, forwards <code>send</code>/<code>throw</code> to it, and evaluates to the sub-generator's <code>return</code> value. It is what lets you split a generator into helper generators."
          },
          {
            "type": "code",
            "src": "def flatten(items):\n    for x in items:\n        if isinstance(x, list):\n            yield from flatten(x)     # recurse, values pass straight up\n        else:\n            yield x\n\nprint(list(flatten([1, [2, [3, 4], 5], [[6]], 7])))\n\ndef read_block(lines):\n    count = 0\n    for line in lines:\n        if line == \"END\":\n            return count              # becomes the value of yield from\n        count += 1\n        yield line.upper()\n\ndef read_all(lines):\n    it = iter(lines)\n    n1 = yield from read_block(it)\n    n2 = yield from read_block(it)\n    yield f\"blocks had {n1} and {n2} lines\"\n\nprint(list(read_all([\"a\", \"b\", \"END\", \"c\", \"END\"])))",
            "label": null,
            "output": "[1, 2, 3, 4, 5, 6, 7]\n['A', 'B', 'C', 'blocks had 2 and 1 lines']",
            "isError": false
          }
        ]
      },
      {
        "title": "The itertools toolkit",
        "body": [
          {
            "type": "p",
            "html": "<code>itertools</code> is a library of lazy building blocks written in C. Knowing a dozen of them replaces most hand-written index loops:"
          },
          {
            "type": "code",
            "src": "from itertools import (accumulate, batched, chain, groupby, islice,\n                       pairwise, product, starmap, tee, zip_longest)\n\nprint(list(chain([1, 2], (3, 4), \"ab\")))\nprint(list(accumulate([3, 1, 4, 1, 5])))            # running sums\nprint(list(accumulate([3, 1, 4, 1, 5], max)))       # running max\nprint(list(pairwise(\"abcd\")))\nprint(list(batched(range(7), 3)))                   # Python 3.12+\nprint(list(zip_longest(\"ab\", \"wxyz\", fillvalue=\"-\")))\nprint(list(starmap(pow, [(2, 3), (10, 2)])))\nprint(list(islice(product(\"ab\", repeat=2), 3)))\n\na, b = tee(iter([1, 2, 3]))                        # two independent copies\nprint(list(a), list(b))",
            "label": null,
            "output": "[1, 2, 3, 4, 'a', 'b']\n[3, 4, 8, 9, 14]\n[3, 3, 4, 4, 5]\n[('a', 'b'), ('b', 'c'), ('c', 'd')]\n[(0, 1, 2), (3, 4, 5), (6,)]\n[('a', 'w'), ('b', 'x'), ('-', 'y'), ('-', 'z')]\n[8, 100]\n[('a', 'a'), ('a', 'b'), ('b', 'a')]\n[1, 2, 3] [1, 2, 3]",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>groupby</code> deserves a warning of its own: it groups <em>consecutive</em> equal keys, like Unix <code>uniq</code>, not all equal keys. Sort by the same key first."
          },
          {
            "type": "code",
            "src": "from itertools import groupby\n\nwords = [\"apple\", \"bob\", \"avocado\", \"banana\", \"cherry\", \"blue\"]\nfirst = lambda w: w[0]\n\nprint([(k, list(g)) for k, g in groupby(words, key=first)])\nprint([(k, list(g)) for k, g in groupby(sorted(words, key=first), key=first)])",
            "label": null,
            "output": "[('a', ['apple']), ('b', ['bob']), ('a', ['avocado']), ('b', ['banana']), ('c', ['cherry']), ('b', ['blue'])]\n[('a', ['apple', 'avocado']), ('b', ['bob', 'banana', 'blue']), ('c', ['cherry'])]",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Need",
              "Reach for"
            ],
            "rows": [
              [
                "First n items / a slice of an iterator",
                "<code>islice(it, n)</code>, <code>islice(it, start, stop, step)</code>"
              ],
              [
                "Concatenate iterables",
                "<code>chain(a, b)</code>, <code>chain.from_iterable(nested)</code>"
              ],
              [
                "Running total / max",
                "<code>accumulate</code>"
              ],
              [
                "Neighbouring pairs",
                "<code>pairwise</code>"
              ],
              [
                "Fixed-size chunks",
                "<code>batched</code> (3.12+)"
              ],
              [
                "Group runs of equal keys",
                "<code>groupby</code> (sort first)"
              ],
              [
                "Cartesian product, permutations, combinations",
                "<code>product</code>, <code>permutations</code>, <code>combinations</code>"
              ],
              [
                "Infinite counters and cycles",
                "<code>count</code>, <code>cycle</code>, <code>repeat</code>"
              ]
            ]
          }
        ]
      },
      {
        "title": "Pitfalls",
        "body": [
          {
            "type": "p",
            "html": "<strong>A generator expression evaluates its first <code>for</code> immediately, and everything else lazily.</strong> The outermost iterable is captured when the expression is created; conditions and other names are looked up when items are pulled."
          },
          {
            "type": "code",
            "src": "data = [1, 2, 3]\nlimit = 2\ngen = (x for x in data if x >= limit)\n\ndata = [10, 20, 30]      # too late: the first `for` already took the old list\nlimit = 3                # not too late: the condition reads `limit` lazily\nprint(list(gen))",
            "label": null,
            "output": "[3]",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>A <code>StopIteration</code> escaping inside a generator is turned into <code>RuntimeError</code></strong> (PEP 479). Before Python 3.7 it silently ended the generator, hiding bugs. A bare <code>next()</code> on an empty iterator inside a generator is the usual culprit."
          },
          {
            "type": "code",
            "src": "def first_of_each(groups):\n    for g in groups:\n        yield next(iter(g))        # raises StopIteration on an empty group\n\ntry:\n    print(list(first_of_each([[1, 2], [], [3]])))\nexcept RuntimeError as e:\n    print(\"RuntimeError:\", e)\n\ndef first_of_each_fixed(groups):\n    for g in groups:\n        first = next(iter(g), None)  # default instead of raising\n        if first is not None:\n            yield first\n\nprint(list(first_of_each_fixed([[1, 2], [], [3]])))",
            "label": null,
            "output": "RuntimeError: generator raised StopIteration\n[1, 3]",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>Generators do not run until iterated.</strong> A function with a <code>yield</code> anywhere in it is a generator, even if that <code>yield</code> is never reached. Calling it for its side effects does nothing."
          },
          {
            "type": "code",
            "src": "def save(records, debug=False):\n    for r in records:\n        print(\"saving\", r)\n    if debug:\n        yield \"debug info\"           # this line makes save() a generator\n\nresult = save([\"a\", \"b\"])            # nothing printed\nprint(type(result).__name__)\nlist(result)                         # now it runs",
            "label": null,
            "output": "generator\nsaving a\nsaving b",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What is the difference between an iterable and an iterator? Is a list an iterator?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "An iterable can produce an iterator (<code>__iter__</code>). An iterator produces values (<code>__next__</code>) and is its own iterable (<code>__iter__</code> returns <code>self</code>). A list is iterable but not an iterator: <code>next([1, 2])</code> is a <code>TypeError</code>, and every <code>for</code> loop over a list gets a fresh <code>list_iterator</code>, which is why lists can be looped over repeatedly while generators cannot."
          },
          {
            "type": "code",
            "src": "from collections.abc import Iterable, Iterator\n\nfor obj in ([1, 2], iter([1, 2]), (x for x in \"ab\"), range(3), open(__file__)):\n    print(f\"{type(obj).__name__:16} iterable={isinstance(obj, Iterable)!s:5} \"\n          f\"iterator={isinstance(obj, Iterator)}\")",
            "label": null,
            "output": "list             iterable=True  iterator=False\nlist_iterator    iterable=True  iterator=True\ngenerator        iterable=True  iterator=True\nrange            iterable=True  iterator=False\nTextIOWrapper    iterable=True  iterator=True",
            "isError": false
          }
        ]
      },
      {
        "q": "Implement <code>range</code>-like iteration for a class two ways: as an iterator class and as a generator. Which would you choose?",
        "level": "medium",
        "answer": [
          {
            "type": "code",
            "src": "class CountUpIterator:\n    \"\"\"Explicit iterator: state lives in attributes.\"\"\"\n    def __init__(self, stop):\n        self.i, self.stop = 0, stop\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.i >= self.stop:\n            raise StopIteration\n        self.i += 1\n        return self.i - 1\n\nclass CountUp:\n    \"\"\"Iterable whose __iter__ is a generator: state lives in the frame.\"\"\"\n    def __init__(self, stop):\n        self.stop = stop\n    def __iter__(self):\n        i = 0\n        while i < self.stop:\n            yield i\n            i += 1\n\nit, c = CountUpIterator(3), CountUp(3)\nprint(list(it), list(it))      # iterator: single use\nprint(list(c), list(c))        # iterable: fresh generator each time",
            "label": null,
            "output": "[0, 1, 2] []\n[0, 1, 2] [0, 1, 2]",
            "isError": false
          },
          {
            "type": "p",
            "html": "Prefer the generator version: it is shorter, cannot forget to raise <code>StopIteration</code>, and making <code>__iter__</code> a generator automatically makes the object re-iterable. Write an explicit iterator class only when the iterator needs extra methods (e.g. <code>peek()</code>, <code>seek()</code>) or must be picklable."
          }
        ]
      },
      {
        "q": "What does this print, and why?",
        "level": "hard",
        "answer": [
          {
            "type": "code",
            "src": "def gen():\n    try:\n        yield 1\n        yield 2\n    finally:\n        print(\"finally\")\n\nfor x in gen():\n    print(x)\n    break\nprint(\"after loop\")",
            "label": null,
            "output": "1\nfinally\nafter loop",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>1</code>, then <code>finally</code>, then <code>after loop</code>. Breaking out of the loop drops the last reference to the generator. CPython frees it immediately, and a generator's finaliser calls <code>close()</code>, which raises <code>GeneratorExit</code> at the paused <code>yield</code> and runs the <code>finally</code>."
          },
          {
            "type": "p",
            "html": "That timing is a CPython reference-counting detail. On PyPy, or if something else still references the generator, the cleanup happens later. If cleanup must happen at a known point, use <code>contextlib.closing(gen())</code> or call <code>gen.close()</code> yourself."
          }
        ]
      },
      {
        "q": "Why can't you use a generator twice, and how do you share one stream between two consumers?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A generator is an iterator; its frame advances and never rewinds. To give two consumers the same stream, either materialise it (<code>list</code>) or use <code>itertools.tee</code>, which buffers items that one copy has seen and the other has not."
          },
          {
            "type": "code",
            "src": "from itertools import tee\n\ndef numbers():\n    for i in range(5):\n        print(f\"  produce {i}\")\n        yield i\n\nevens_src, odds_src = tee(numbers())\nevens = [x for x in evens_src if x % 2 == 0]   # pulls everything once\nodds = [x for x in odds_src if x % 2]          # served from tee's buffer\nprint(evens, odds)",
            "label": null,
            "output": "  produce 0\n  produce 1\n  produce 2\n  produce 3\n  produce 4\n[0, 2, 4] [1, 3]",
            "isError": false
          },
          {
            "type": "p",
            "html": "Each value was produced once. The cost: <code>tee</code> keeps everything that one copy has consumed and the other has not. If one consumer runs all the way ahead, that is the whole stream in memory &mdash; in which case <code>list()</code> is simpler and no worse."
          }
        ]
      },
      {
        "q": "What does <code>yield from</code> do that a <code>for</code> loop with <code>yield</code> doesn't?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "For plain iteration they are equivalent. The differences show up with two-way generators: <code>yield from</code> forwards <code>send()</code> and <code>throw()</code> into the sub-generator, calls its <code>close()</code> correctly, and evaluates to the sub-generator's <code>return</code> value. A <code>for</code> loop drops all of that."
          },
          {
            "type": "code",
            "src": "def inner():\n    received = yield \"ready\"\n    return f\"inner got {received}\"\n\ndef with_yield_from():\n    result = yield from inner()\n    yield result\n\ndef with_for_loop():\n    for v in inner():\n        yield v\n    yield \"return value is lost\"\n\nfor outer in (with_yield_from, with_for_loop):\n    g = outer()\n    print(next(g), \"->\", g.send(\"hello\"))",
            "label": null,
            "output": "ready -> inner got hello\nready -> return value is lost",
            "isError": false
          },
          {
            "type": "p",
            "html": "In the <code>for</code> version, <code>send(\"hello\")</code> went to the <em>outer</em> generator's <code>yield</code>. The loop then called <code>next()</code> on <code>inner</code>, so <code>received</code> was <code>None</code>, and <code>inner</code>'s return value vanished inside the loop's <code>StopIteration</code>."
          }
        ]
      },
      {
        "q": "You need to read a 20 GB CSV and write the rows that match a filter, transformed, to a new file. Sketch the design.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A pipeline of generators: a reader that yields rows from the open file (files are already lazy iterators over lines), a filter stage, a transform stage, and a writer that consumes the pipeline. Memory stays at one row plus buffers, no matter how big the file is; each stage is separately testable with a list as input."
          },
          {
            "type": "code",
            "src": "import csv, io\n\nsource = io.StringIO(\"id,amount\\n1,50\\n2,700\\n3,1200\\n4,30\\n\")\nsink = io.StringIO()\n\ndef read_rows(f):\n    yield from csv.DictReader(f)\n\ndef large(rows, threshold):\n    return (r for r in rows if int(r[\"amount\"]) >= threshold)\n\ndef with_fee(rows):\n    for r in rows:\n        yield {**r, \"fee\": round(int(r[\"amount\"]) * 0.02, 2)}\n\ndef write(rows, f):\n    w = None\n    for n, r in enumerate(rows, 1):\n        if w is None:\n            w = csv.DictWriter(f, fieldnames=list(r))\n            w.writeheader()\n        w.writerow(r)\n    return n if w else 0\n\nprint(\"rows written:\", write(with_fee(large(read_rows(source), 500)), sink))\nprint(sink.getvalue().strip())",
            "label": null,
            "output": "rows written: 2\nid,amount,fee\n2,700,14.0\n3,1200,24.0",
            "isError": false
          },
          {
            "type": "p",
            "html": "Things to mention: <code>csv</code> handles quoting so do not split on commas yourself; open files with <code>newline=\"\"</code> for <code>csv</code>; and the pipeline is single-pass, so counting rows has to happen inside a stage, as <code>write</code> does here."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: Iterator types",
        "url": "https://docs.python.org/3/library/stdtypes.html#iterator-types"
      },
      {
        "label": "Python docs: Generator expressions and yield",
        "url": "https://docs.python.org/3/reference/expressions.html#yield-expressions"
      },
      {
        "label": "Python docs: itertools",
        "url": "https://docs.python.org/3/library/itertools.html"
      },
      {
        "label": "PEP 479: Change StopIteration handling inside generators",
        "url": "https://peps.python.org/pep-0479/"
      },
      {
        "label": "PEP 380: Syntax for delegating to a subgenerator",
        "url": "https://peps.python.org/pep-0380/"
      }
    ]
  },
  {
    "id": "context-managers",
    "title": "Context Managers",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "A <code>with</code> block guarantees that setup is paired with teardown, whether the block finishes normally, returns early, or raises. Files get closed, locks get released, transactions get committed or rolled back. The object that provides the setup and teardown is a <strong>context manager</strong>, and the protocol behind it is two methods: <code>__enter__</code> and <code>__exit__</code>.",
      "This page covers exactly what <code>with</code> expands to, how exceptions flow through <code>__exit__</code> and how to suppress them, writing managers as classes and as generators, managing a dynamic number of them with <code>ExitStack</code>, and the async version."
    ],
    "sections": [
      {
        "title": "The protocol, and what with expands to",
        "body": [
          {
            "type": "p",
            "html": "<code>with EXPR as VAR: BODY</code> is roughly this <code>try/finally</code>, written out by hand:"
          },
          {
            "type": "code",
            "src": "import sys\n\nclass Demo:\n    def __enter__(self):\n        print(\"enter\")\n        return \"the value bound by 'as'\"\n    def __exit__(self, exc_type, exc, tb):\n        print(f\"exit  exc_type={exc_type.__name__ if exc_type else None}\")\n        return False                 # do not suppress\n\n# with Demo() as value: print(value)   is equivalent to:\nmanager = Demo()\nvalue = type(manager).__enter__(manager)\ntry:\n    print(value)\nexcept BaseException:\n    if not type(manager).__exit__(manager, *sys.exc_info()):\n        raise\nelse:\n    type(manager).__exit__(manager, None, None, None)",
            "label": null,
            "output": "enter\nthe value bound by 'as'\nexit  exc_type=None",
            "isError": false
          },
          {
            "type": "p",
            "html": "Four details fall out of the expansion:"
          },
          {
            "type": "table",
            "head": [
              "Detail",
              "Consequence"
            ],
            "rows": [
              [
                "<code>as</code> binds what <code>__enter__</code> <em>returns</em>",
                "Not necessarily the manager. <code>open()</code> returns <code>self</code>; a lock returns <code>True</code>; <code>decimal.localcontext()</code> returns a new context"
              ],
              [
                "<code>__exit__</code> gets the exception triple",
                "<code>(None, None, None)</code> on success; type, instance and traceback on failure"
              ],
              [
                "A truthy return from <code>__exit__</code> swallows the exception",
                "Execution continues after the <code>with</code> block"
              ],
              [
                "<code>__enter__</code> runs <em>before</em> the <code>try</code>",
                "If <code>__enter__</code> raises, <code>__exit__</code> is never called"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Like other special methods, <code>__enter__</code> and <code>__exit__</code> are looked up on the type, not the instance."
          }
        ]
      },
      {
        "title": "A class-based context manager",
        "body": [
          {
            "type": "p",
            "html": "Class-based managers are the right choice when the manager has state you want to inspect afterwards, or is reusable. A timer is the classic example:"
          },
          {
            "type": "code",
            "src": "import time\n\nclass Timer:\n    def __enter__(self):\n        self.start = time.perf_counter()\n        return self\n    def __exit__(self, exc_type, exc, tb):\n        self.elapsed = time.perf_counter() - self.start\n        return False\n\nwith Timer() as t:\n    sum(range(100_000))\n\nprint(\"measured something:\", t.elapsed > 0)\nprint(\"t is still usable after the block:\", hasattr(t, \"elapsed\"))",
            "label": null,
            "output": "measured something: True\nt is still usable after the block: True",
            "isError": false
          },
          {
            "type": "p",
            "html": "Names bound inside or by a <code>with</code> are ordinary local variables &mdash; the block does not create a scope, so <code>t</code> is still there afterwards."
          }
        ]
      },
      {
        "title": "Exceptions and suppression",
        "body": [
          {
            "type": "p",
            "html": "<code>__exit__</code> sees every exception that leaves the block and decides whether it propagates. Returning <code>True</code> suppresses it. Be selective: swallowing everything hides bugs."
          },
          {
            "type": "code",
            "src": "class Ignore:\n    def __init__(self, *types):\n        self.types = types\n    def __enter__(self):\n        return self\n    def __exit__(self, exc_type, exc, tb):\n        if exc_type is not None and issubclass(exc_type, self.types):\n            print(f\"  suppressed {exc_type.__name__}: {exc}\")\n            return True\n        return False\n\nwith Ignore(KeyError):\n    {}[\"missing\"]\n    print(\"never printed\")\nprint(\"carried on after KeyError\")\n\ntry:\n    with Ignore(KeyError):\n        1 / 0\nexcept ZeroDivisionError:\n    print(\"ZeroDivisionError still propagated\")",
            "label": null,
            "output": "  suppressed KeyError: 'missing'\ncarried on after KeyError\nZeroDivisionError still propagated",
            "isError": false
          },
          {
            "type": "p",
            "html": "The standard library already has this as <code>contextlib.suppress</code>. Note that the rest of the block is skipped &mdash; suppression resumes <em>after</em> the <code>with</code>, not after the failing line."
          },
          {
            "type": "code",
            "src": "import contextlib, os\n\nwith contextlib.suppress(FileNotFoundError):\n    os.remove(\"does-not-exist.tmp\")\nprint(\"no error, no if-exists race\")",
            "label": null,
            "output": "no error, no if-exists race",
            "isError": false
          },
          {
            "type": "p",
            "html": "That pattern is better than <code>if os.path.exists(p): os.remove(p)</code>, which has a race between the check and the remove."
          }
        ]
      },
      {
        "title": "Generator-based: contextlib.contextmanager",
        "body": [
          {
            "type": "p",
            "html": "For simple setup/teardown pairs, write a generator that yields once. Code before the <code>yield</code> is <code>__enter__</code>, the yielded value is what <code>as</code> binds, and code after is <code>__exit__</code>. If the block raises, the exception is re-raised <em>at the yield</em>."
          },
          {
            "type": "code",
            "src": "from contextlib import contextmanager\n\n@contextmanager\ndef tag(name):\n    print(f\"<{name}>\")\n    try:\n        yield name.upper()\n    finally:\n        print(f\"</{name}>\")\n\nwith tag(\"div\") as t:\n    print(\"  content\", t)\n\ntry:\n    with tag(\"p\"):\n        raise ValueError(\"boom\")\nexcept ValueError as e:\n    print(\"caught\", e)",
            "label": null,
            "output": "<div>\n  content DIV\n</div>\n<p>\n</p>\ncaught boom",
            "isError": false
          },
          {
            "type": "p",
            "html": "The <code>try/finally</code> is not optional. Without it, an exception in the block is raised at the <code>yield</code> and the cleanup line after it never runs:"
          },
          {
            "type": "code",
            "src": "from contextlib import contextmanager\n\n@contextmanager\ndef lock_file():\n    print(\"acquire\")\n    yield\n    print(\"release\")          # skipped if the block raises\n\ntry:\n    with lock_file():\n        raise RuntimeError(\"oops\")\nexcept RuntimeError:\n    pass\nprint(\"the lock was never released\")",
            "label": "the bug",
            "output": "acquire\nthe lock was never released",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "",
              "Class with <code>__enter__</code>/<code>__exit__</code>",
              "<code>@contextmanager</code> generator"
            ],
            "rows": [
              [
                "Brevity",
                "More boilerplate",
                "Short; setup and teardown read top to bottom"
              ],
              [
                "State after the block",
                "Natural (attributes on <code>self</code>)",
                "Awkward (yield a mutable object)"
              ],
              [
                "Reusable / re-entrant",
                "Can be",
                "Single use: a generator can only run once"
              ],
              [
                "Suppressing exceptions",
                "Return <code>True</code>",
                "Catch it around the <code>yield</code> and do not re-raise"
              ],
              [
                "Also works as a decorator",
                "Subclass <code>ContextDecorator</code>",
                "Yes, automatically"
              ]
            ]
          }
        ]
      },
      {
        "title": "Several managers, and a dynamic number: ExitStack",
        "body": [
          {
            "type": "p",
            "html": "One <code>with</code> can hold several managers; they are entered left to right and exited right to left. Since 3.10 you can wrap them in parentheses across lines."
          },
          {
            "type": "code",
            "src": "from contextlib import contextmanager\n\n@contextmanager\ndef res(name):\n    print(\"open \", name)\n    try:\n        yield name\n    finally:\n        print(\"close\", name)\n\nwith (\n    res(\"db\") as db,\n    res(\"cache\") as cache,\n):\n    print(\"using\", db, cache)",
            "label": null,
            "output": "open  db\nopen  cache\nusing db cache\nclose cache\nclose db",
            "isError": false
          },
          {
            "type": "p",
            "html": "When the number of resources is only known at run time, use <code>ExitStack</code>. It is a context manager that holds other context managers, and unwinds all of them &mdash; even if opening the fourth one fails after three succeeded."
          },
          {
            "type": "code",
            "src": "from contextlib import ExitStack, contextmanager\n\n@contextmanager\ndef res(name):\n    if name == \"bad\":\n        raise OSError(f\"cannot open {name}\")\n    print(\"open \", name)\n    try:\n        yield name\n    finally:\n        print(\"close\", name)\n\ndef open_all(names):\n    with ExitStack() as stack:\n        handles = [stack.enter_context(res(n)) for n in names]\n        stack.callback(print, \"callback runs too\")\n        print(\"all open:\", handles)\n\nopen_all([\"a\", \"b\", \"c\"])\nprint(\"---\")\ntry:\n    open_all([\"a\", \"b\", \"bad\", \"d\"])\nexcept OSError as e:\n    print(\"OSError:\", e)",
            "label": null,
            "output": "open  a\nopen  b\nopen  c\nall open: ['a', 'b', 'c']\ncallback runs too\nclose c\nclose b\nclose a\n---\nopen  a\nopen  b\nclose b\nclose a\nOSError: cannot open bad",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>stack.pop_all()</code> transfers everything to a new stack, which is the idiom for &ldquo;open several resources, and only if all succeed, hand them to the caller&rdquo;."
          }
        ]
      },
      {
        "title": "Async context managers",
        "body": [
          {
            "type": "p",
            "html": "<code>async with</code> uses <code>__aenter__</code> and <code>__aexit__</code>, which are coroutines, so setup and teardown can await &mdash; opening a connection, starting a transaction, acquiring an <code>asyncio.Lock</code>."
          },
          {
            "type": "code",
            "src": "import asyncio\nfrom contextlib import asynccontextmanager\n\nclass Connection:\n    async def __aenter__(self):\n        await asyncio.sleep(0)            # pretend network I/O\n        print(\"connected\")\n        return self\n    async def __aexit__(self, exc_type, exc, tb):\n        await asyncio.sleep(0)\n        print(\"disconnected\")\n        return False\n\n@asynccontextmanager\nasync def transaction(conn):\n    print(\"  BEGIN\")\n    try:\n        yield\n        print(\"  COMMIT\")\n    except Exception:\n        print(\"  ROLLBACK\")\n        raise\n\nasync def main():\n    async with Connection() as conn:\n        async with transaction(conn):\n            print(\"  insert row\")\n\nasyncio.run(main())",
            "label": null,
            "output": "connected\n  BEGIN\n  insert row\n  COMMIT\ndisconnected",
            "isError": false
          }
        ]
      },
      {
        "title": "Useful managers from the standard library",
        "body": [
          {
            "type": "table",
            "head": [
              "Manager",
              "Sets up",
              "Tears down"
            ],
            "rows": [
              [
                "<code>open(...)</code>",
                "Opens a file",
                "Closes it"
              ],
              [
                "<code>threading.Lock()</code>",
                "Acquires",
                "Releases"
              ],
              [
                "<code>contextlib.suppress(*exc)</code>",
                "&mdash;",
                "Swallows the listed exceptions"
              ],
              [
                "<code>contextlib.redirect_stdout(f)</code>",
                "Points <code>sys.stdout</code> at <code>f</code>",
                "Restores it"
              ],
              [
                "<code>contextlib.chdir(path)</code> (3.11+)",
                "Changes directory",
                "Changes back"
              ],
              [
                "<code>contextlib.nullcontext(x)</code>",
                "Nothing; <code>as</code> gets <code>x</code>",
                "Nothing &mdash; for optional managers"
              ],
              [
                "<code>contextlib.closing(obj)</code>",
                "&mdash;",
                "Calls <code>obj.close()</code>"
              ],
              [
                "<code>decimal.localcontext()</code>",
                "Copies the decimal context",
                "Restores precision and rounding"
              ],
              [
                "<code>tempfile.TemporaryDirectory()</code>",
                "Creates a directory",
                "Deletes it and its contents"
              ],
              [
                "<code>unittest.mock.patch(...)</code>",
                "Replaces an attribute",
                "Restores the original"
              ]
            ]
          },
          {
            "type": "code",
            "src": "import io, contextlib, decimal\n\nbuffer = io.StringIO()\nwith contextlib.redirect_stdout(buffer):\n    print(\"captured, not shown\")\nprint(\"captured:\", repr(buffer.getvalue()))\n\nwith decimal.localcontext() as ctx:\n    ctx.prec = 5\n    print(decimal.Decimal(1) / decimal.Decimal(7))\nprint(decimal.Decimal(1) / decimal.Decimal(7))\n\ndef process(path=None):\n    cm = open(path) if path else contextlib.nullcontext(io.StringIO(\"default\"))\n    with cm as f:\n        return f.read()\nprint(process())",
            "label": null,
            "output": "captured: 'captured, not shown\\n'\n0.14286\n0.1428571428571428571428571429\ndefault",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "If <code>__enter__</code> raises, is <code>__exit__</code> called? What if the body raises and then <code>__exit__</code> raises too?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "No. <code>__enter__</code> runs before the implicit <code>try</code>, so a failing <code>__enter__</code> means the resource was never acquired and there is nothing to exit. Any partial setup must be cleaned up inside <code>__enter__</code> itself."
          },
          {
            "type": "p",
            "html": "If the body raises and <code>__exit__</code> also raises, the new exception replaces the original, with the original attached as <code>__context__</code> (&ldquo;During handling of the above exception, another exception occurred&rdquo;)."
          },
          {
            "type": "code",
            "src": "class Fragile:\n    def __enter__(self):\n        return self\n    def __exit__(self, *exc):\n        raise RuntimeError(\"cleanup failed\")\n\ntry:\n    with Fragile():\n        raise ValueError(\"original problem\")\nexcept Exception as e:\n    print(type(e).__name__, \"-\", e)\n    print(\"context:\", repr(e.__context__))",
            "label": null,
            "output": "RuntimeError - cleanup failed\ncontext: ValueError('original problem')",
            "isError": false
          },
          {
            "type": "p",
            "html": "That is why teardown code should be as simple and failure-proof as possible, and why <code>ExitStack</code> goes to great lengths to keep running every remaining callback even when one fails."
          }
        ]
      },
      {
        "q": "Write a transaction context manager that commits on success and rolls back on any exception.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Decide on the path by whether an exception arrived, and do not suppress it: the caller needs to know the transaction failed."
          },
          {
            "type": "code",
            "src": "class FakeDB:\n    def __init__(self): self.data, self.pending = {}, None\n    def begin(self): self.pending = dict(self.data)\n    def commit(self): self.data, self.pending = self.pending, None\n    def rollback(self): self.pending = None\n\nclass transaction:\n    def __init__(self, db): self.db = db\n    def __enter__(self):\n        self.db.begin()\n        return self.db.pending\n    def __exit__(self, exc_type, exc, tb):\n        if exc_type is None:\n            self.db.commit()\n        else:\n            self.db.rollback()\n        return False                       # let the error propagate\n\ndb = FakeDB()\nwith transaction(db) as t:\n    t[\"alice\"] = 100\nprint(db.data)\n\ntry:\n    with transaction(db) as t:\n        t[\"alice\"] = 0\n        raise ValueError(\"payment declined\")\nexcept ValueError as e:\n    print(\"failed:\", e, \"| data unchanged:\", db.data)",
            "label": null,
            "output": "{'alice': 100}\nfailed: payment declined | data unchanged: {'alice': 100}",
            "isError": false
          },
          {
            "type": "p",
            "html": "Follow-ups: nested transactions (savepoints &mdash; keep a depth counter and only commit at depth zero), and what happens if <code>commit()</code> itself raises (the exception propagates from <code>__exit__</code>, which is correct: the caller must know)."
          }
        ]
      },
      {
        "q": "Why must a <code>@contextmanager</code> generator wrap its <code>yield</code> in <code>try/finally</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Because when the <code>with</code> body raises, <code>contextmanager</code> calls <code>generator.throw(exc)</code>, and the exception appears to come from the <code>yield</code> line. Anything after the <code>yield</code> that is not in a <code>finally</code> (or an <code>except</code>) is skipped, so the teardown never happens. A <code>finally</code> runs on success, on exceptions, and even when the block exits via <code>return</code> or <code>break</code>."
          },
          {
            "type": "p",
            "html": "If you want to <em>suppress</em> an exception in a generator-based manager, catch it around the <code>yield</code> and do not re-raise. If you catch it and forget to re-raise when you did not mean to suppress, you have silently swallowed errors &mdash; a surprisingly common bug."
          }
        ]
      },
      {
        "q": "How do you open an unknown number of files safely, so that all are closed even if opening one of them fails?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "<code>contextlib.ExitStack</code>. Each <code>enter_context</code> call enters a manager and registers its exit. If a later <code>open</code> raises, the <code>with ExitStack()</code> block unwinds, closing every file opened so far in reverse order."
          },
          {
            "type": "code",
            "src": "import contextlib, pathlib, tempfile\n\nwith tempfile.TemporaryDirectory() as d:\n    paths = [pathlib.Path(d, f\"part{i}.txt\") for i in range(3)]\n    for i, p in enumerate(paths):\n        p.write_text(f\"chunk {i}\\n\")\n\n    with contextlib.ExitStack() as stack:\n        files = [stack.enter_context(open(p)) for p in paths]\n        merged = \"\".join(f.read() for f in files)\n    print(merged, end=\"\")\n    print(\"all closed:\", all(f.closed for f in files))\n\n    missing = paths + [pathlib.Path(d, \"nope.txt\")]\n    try:\n        with contextlib.ExitStack() as stack:\n            files = []\n            for p in missing:\n                files.append(stack.enter_context(open(p)))\n    except FileNotFoundError:\n        print(\"failed on the 4th; first 3 closed:\", all(f.closed for f in files))",
            "label": null,
            "output": "chunk 0\nchunk 1\nchunk 2\nall closed: True\nfailed on the 4th; first 3 closed: True",
            "isError": false
          },
          {
            "type": "p",
            "html": "Writing this with nested <code>with</code> statements is impossible for an unknown count, and doing it with a manual list and <code>try/finally</code> is easy to get subtly wrong (a failing <code>close</code> can skip the rest)."
          }
        ]
      },
      {
        "q": "Can a context manager be reused or re-entered? Give examples of each.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Three categories:"
          },
          {
            "type": "p",
            "html": "<strong>Single-use</strong>: can be entered once. Generator-based managers (<code>@contextmanager</code>) &mdash; the generator has already run &mdash; and file objects returned by <code>open</code>, which are closed after the first block.<br><strong>Reusable</strong>: can be used in several <code>with</code> statements one after another, but not nested. <code>threading.Lock</code> is reusable; nesting it on the same thread deadlocks.<br><strong>Re-entrant</strong>: can be nested inside itself. <code>threading.RLock</code>, <code>contextlib.suppress</code>, <code>redirect_stdout</code>."
          },
          {
            "type": "code",
            "src": "from contextlib import contextmanager\nimport threading\n\n@contextmanager\ndef once():\n    yield\n\ncm = once()\nwith cm: pass\ntry:\n    with cm: pass\nexcept (RuntimeError, AttributeError) as e:\n    print(\"second use failed with\", type(e).__name__)\n\nrlock = threading.RLock()\nwith rlock:\n    with rlock:\n        print(\"RLock nested fine\")\n\nlock = threading.Lock()\nwith lock:\n    print(\"Lock acquired again while held?\", lock.acquire(blocking=False))",
            "label": null,
            "output": "second use failed with AttributeError\nRLock nested fine\nLock acquired again while held? False",
            "isError": false
          }
        ]
      },
      {
        "q": "Implement a timing context manager that also works as a decorator.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Subclass <code>contextlib.ContextDecorator</code>: it adds a <code>__call__</code> that wraps the function body in <code>with self:</code>. Generator managers from <code>@contextmanager</code> get this for free."
          },
          {
            "type": "code",
            "src": "import time\nfrom contextlib import ContextDecorator\n\nclass timed(ContextDecorator):\n    def __init__(self, label):\n        self.label = label\n    def __enter__(self):\n        self.start = time.perf_counter()\n        return self\n    def __exit__(self, *exc):\n        ms = (time.perf_counter() - self.start) * 1000\n        print(f\"{self.label}: finished, under 1000 ms: {ms < 1000}\")\n        return False\n\nwith timed(\"block\"):\n    sum(range(10_000))\n\n@timed(\"function\")\ndef work():\n    return sum(range(10_000))\n\nprint(work())",
            "label": null,
            "output": "block: finished, under 1000 ms: True\nfunction: finished, under 1000 ms: True\n49995000",
            "isError": false
          },
          {
            "type": "p",
            "html": "One subtlety: when used as a decorator the same manager instance is entered on every call, so it must not keep per-call state that breaks under recursion or concurrent calls."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "PEP 343 — The with statement",
        "url": "https://peps.python.org/pep-0343/"
      },
      {
        "label": "Python docs: contextlib",
        "url": "https://docs.python.org/3/library/contextlib.html"
      },
      {
        "label": "Python docs: With statement context managers",
        "url": "https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers"
      }
    ]
  },
  {
    "id": "import-system",
    "title": "The Import System",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "<code>import x</code> looks like a declaration, but it is an ordinary statement that runs at run time: it finds a file, executes it top to bottom to build a module object, caches that object, and binds a name. Almost every confusing import bug &mdash; circular imports, a change that &ldquo;didn&rsquo;t take&rdquo;, a module imported twice, <code>from x import y</code> seeing a stale value &mdash; follows directly from those four steps.",
      "This topic walks through the steps, then through packages, relative imports, circular imports, <code>__main__</code>, reloading, lazy loading and finally the hooks that let you import from anywhere."
    ],
    "sections": [
      {
        "title": "What import actually does",
        "body": [
          {
            "type": "p",
            "html": "<code>import spam</code> does this:"
          },
          {
            "type": "p",
            "html": "1. Look in <code>sys.modules</code>. If <code>\"spam\"</code> is there, use that object and stop.<br>2. Otherwise ask each <em>finder</em> on <code>sys.meta_path</code> for a <em>module spec</em> (where it is, how to load it).<br>3. Create an empty module object, <strong>put it in <code>sys.modules</code> first</strong>, then execute the module's code with that object's <code>__dict__</code> as globals.<br>4. Bind the name <code>spam</code> in the importing namespace."
          },
          {
            "type": "code",
            "src": "import sys, tempfile, pathlib\n\ntmp = pathlib.Path(tempfile.mkdtemp())\n(tmp / \"spam.py\").write_text(\n    'print(\"  executing spam.py\")\\n'\n    'value = 42\\n'\n)\nsys.path.insert(0, str(tmp))\n\nprint(\"in cache before:\", \"spam\" in sys.modules)\nimport spam\nprint(\"in cache after: \", \"spam\" in sys.modules)\nimport spam                        # cache hit: nothing printed\nimport spam as again\nprint(again is spam is sys.modules[\"spam\"], spam.value)\nprint(type(spam).__name__, spam.__name__, spam.__spec__.loader.__class__.__name__)",
            "label": null,
            "output": "in cache before: False\n  executing spam.py\nin cache after:  True\nTrue 42\nmodule spam SourceFileLoader",
            "isError": false
          },
          {
            "type": "p",
            "html": "Module code runs <strong>once per process</strong>, however many times and from however many files it is imported. That is why module-level code is the natural place for configuration and singletons, and also why expensive work at import time slows down every program that touches the module."
          },
          {
            "type": "note",
            "text": "A module is just an object whose attributes are its global variables. <code>spam.value</code> is <code>spam.__dict__[\"value\"]</code>."
          }
        ]
      },
      {
        "title": "import x vs from x import y",
        "body": [
          {
            "type": "p",
            "html": "<code>import x</code> binds the module. <code>from x import y</code> imports the module the same way, then copies the <em>current</em> value of <code>x.y</code> into a new local name. If <code>x</code> later rebinds <code>y</code>, your copy does not change."
          },
          {
            "type": "code",
            "src": "import sys, tempfile, pathlib\ntmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))\n\n(tmp / \"settings.py\").write_text(\n    \"debug = False\\n\"\n    \"def enable():\\n\"\n    \"    global debug\\n\"\n    \"    debug = True\\n\"\n)\n\nimport settings\nfrom settings import debug           # a copy of the binding, taken now\n\nsettings.enable()\nprint(\"settings.debug:\", settings.debug)   # reads the module's current value\nprint(\"debug:         \", debug)            # still the old object",
            "label": null,
            "output": "settings.debug: True\ndebug:          False",
            "isError": false
          },
          {
            "type": "p",
            "html": "This is also why monkeypatching in tests has to target the module that <em>uses</em> a name. If <code>app.py</code> did <code>from time import sleep</code>, patching <code>time.sleep</code> does nothing to <code>app.sleep</code>; patch <code>app.sleep</code> instead."
          },
          {
            "type": "table",
            "head": [
              "Form",
              "Binds",
              "Sees later rebinding?"
            ],
            "rows": [
              [
                "<code>import pkg.mod</code>",
                "<code>pkg</code> (the top-level package)",
                "Yes, via <code>pkg.mod.name</code>"
              ],
              [
                "<code>import pkg.mod as m</code>",
                "<code>m</code> = the submodule",
                "Yes, via <code>m.name</code>"
              ],
              [
                "<code>from pkg.mod import name</code>",
                "<code>name</code> = the object right now",
                "No"
              ],
              [
                "<code>from pkg import mod</code>",
                "<code>mod</code> = the submodule",
                "Yes, via <code>mod.name</code>"
              ]
            ]
          }
        ]
      },
      {
        "title": "Where Python looks: sys.path and finders",
        "body": [
          {
            "type": "p",
            "html": "The default finders search <code>sys.path</code> in order: the script's directory (or the current directory for <code>-m</code> and the REPL), <code>PYTHONPATH</code>, the standard library, then <code>site-packages</code>. The first match wins, which is how a local file called <code>random.py</code> or <code>email.py</code> breaks the standard library module with the same name."
          },
          {
            "type": "code",
            "src": "import sys, importlib.util\n\nprint([getattr(f, \"__name__\", type(f).__name__) for f in sys.meta_path])\n\nfor name in (\"json\", \"math\", \"sys\", \"os\", \"not_a_real_module\"):\n    spec = importlib.util.find_spec(name)\n    if spec is None:\n        print(f\"{name:18} not found\")\n        continue\n    loader = getattr(spec.loader, \"__name__\", type(spec.loader).__name__)\n    kind = spec.origin if spec.origin in (\"built-in\", \"frozen\") else spec.origin.rsplit(\".\", 1)[-1]\n    print(f\"{name:18} loader={loader:22} origin={kind}\")",
            "label": null,
            "output": "['BuiltinImporter', 'FrozenImporter', 'PathFinder']\njson               loader=SourceFileLoader       origin=py\nmath               loader=ExtensionFileLoader    origin=so\nsys                loader=BuiltinImporter        origin=built-in\nos                 loader=FrozenImporter         origin=frozen\nnot_a_real_module  not found",
            "isError": false
          },
          {
            "type": "p",
            "html": "Built-in modules like <code>sys</code> are compiled into the interpreter; <code>math</code> is usually a C extension (<code>.so</code>/<code>.pyd</code>); <code>json</code> is a package of <code>.py</code> files. All three come back as the same kind of module object."
          },
          {
            "type": "caveat",
            "text": "CPython also <em>freezes</em> a few startup modules (like <code>os</code> and <code>codecs</code>) into the binary for faster start-up, so their spec says <code>frozen</code> rather than pointing at a file."
          }
        ]
      },
      {
        "title": "Packages and relative imports",
        "body": [
          {
            "type": "p",
            "html": "A <strong>package</strong> is a module with a <code>__path__</code>: a directory that can contain submodules. Importing <code>pkg.sub</code> imports <code>pkg</code> first (running its <code>__init__.py</code>), then <code>pkg.sub</code>, and sets <code>sub</code> as an attribute on <code>pkg</code>. A directory without <code>__init__.py</code> still imports, as a <em>namespace package</em> that can be spread across several directories."
          },
          {
            "type": "code",
            "src": "import sys, tempfile, pathlib\ntmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))\n\npkg = tmp / \"shop\"; (pkg / \"models\").mkdir(parents=True)\n(pkg / \"__init__.py\").write_text('print(\"  init shop\")\\nVERSION = \"1.0\"\\n')\n(pkg / \"models\" / \"__init__.py\").write_text('print(\"  init shop.models\")\\n')\n(pkg / \"models\" / \"order.py\").write_text(\n    \"from .. import VERSION          # up one package\\n\"\n    \"from . import line              # sibling module\\n\"\n    \"def describe():\\n\"\n    \"    return f'order v{VERSION} with {line.KIND}'\\n\"\n)\n(pkg / \"models\" / \"line.py\").write_text('KIND = \"line items\"\\n')\n\nimport shop.models.order\nprint(shop.models.order.describe())\nprint(shop.models.order.__package__, \"|\", \"shop.models.line\" in sys.modules)\nprint(hasattr(shop, \"__path__\"), hasattr(shop.models.order, \"__path__\"))",
            "label": null,
            "output": "  init shop\n  init shop.models\norder v1.0 with line items\nshop.models | True\nTrue False",
            "isError": false
          },
          {
            "type": "p",
            "html": "Relative imports resolve against the module's <code>__package__</code>, not against the file system. A file run directly as a script has <code>__name__ == \"__main__\"</code> and no package, so its relative imports fail. Run it as a module instead: <code>python -m shop.models.order</code>."
          },
          {
            "type": "code",
            "src": "import subprocess, sys, tempfile, pathlib\ntmp = pathlib.Path(tempfile.mkdtemp())\n(tmp / \"app\").mkdir()\n(tmp / \"app\" / \"__init__.py\").write_text(\"\")\n(tmp / \"app\" / \"util.py\").write_text(\"NAME = 'util'\\n\")\n(tmp / \"app\" / \"main.py\").write_text(\n    \"from .util import NAME\\nprint('ok, imported', NAME, 'as', __name__)\\n\")\n\ndef run(*args):\n    p = subprocess.run([sys.executable, *args], cwd=tmp, capture_output=True, text=True)\n    return (p.stdout or p.stderr.strip().splitlines()[-1]).strip()\n\nprint(\"python app/main.py ->\", run(\"app/main.py\"))\nprint(\"python -m app.main ->\", run(\"-m\", \"app.main\"))",
            "label": null,
            "output": "python app/main.py -> ImportError: attempted relative import with no known parent package\npython -m app.main -> ok, imported util as __main__",
            "isError": false
          }
        ]
      },
      {
        "title": "Circular imports",
        "body": [
          {
            "type": "p",
            "html": "Step 3 above is the key to circular imports: a module is placed in <code>sys.modules</code> <em>before</em> its code runs. If <code>a</code> imports <code>b</code> and <code>b</code> imports <code>a</code>, the second import does not loop forever &mdash; it gets the half-built <code>a</code> from the cache. Anything <code>a</code> has not defined yet is missing."
          },
          {
            "type": "code",
            "src": "import sys, tempfile, pathlib\ntmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))\n\n(tmp / \"orders.py\").write_text(\n    \"import customers\\n\"\n    \"def total(): return 100\\n\"\n)\n(tmp / \"customers.py\").write_text(\n    \"from orders import total     # orders is only half executed\\n\"\n    \"def spend(): return total()\\n\"\n)\ntry:\n    import orders\nexcept ImportError as e:\n    print(\"ImportError:\", str(e).rsplit(\" (/\", 1)[0])    # drop the temp path",
            "label": null,
            "output": "ImportError: cannot import name 'total' from partially initialized module 'orders' (most likely due to a circular import)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Recent Python versions even name the cause in the message (&ldquo;most likely due to a circular import&rdquo;). There are three standard fixes, in order of preference:"
          },
          {
            "type": "p",
            "html": "1. <strong>Restructure</strong>: move what both modules need into a third module that imports neither.<br>2. <strong>Import the module, not the name</strong>: <code>import orders</code> and call <code>orders.total()</code> inside the function, so the lookup happens at call time, after both modules have finished.<br>3. <strong>Import inside the function</strong> that needs it, deferring the import until it runs."
          },
          {
            "type": "code",
            "src": "import sys, tempfile, pathlib\ntmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))\n\n(tmp / \"orders.py\").write_text(\n    \"import customers\\n\"\n    \"def total(): return 100\\n\"\n)\n(tmp / \"customers.py\").write_text(\n    \"import orders                  # just the (half-built) module object\\n\"\n    \"def spend(): return orders.total() * 2   # looked up at call time\\n\"\n)\nimport orders, customers\nprint(customers.spend())",
            "label": null,
            "output": "200",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "<code>from typing import TYPE_CHECKING</code> plus <code>if TYPE_CHECKING: from orders import Order</code> is the usual way to break a cycle that exists only for type hints: the import runs for the type checker, never at run time."
          }
        ]
      },
      {
        "title": "__name__, __main__ and the double-import trap",
        "body": [
          {
            "type": "p",
            "html": "The file you run is executed as the module <code>__main__</code>, not under its file name. If another module then imports it by name, Python finds no <code>\"script\"</code> in <code>sys.modules</code> and executes the file a <em>second</em> time as a separate module. Two copies means two sets of globals and two different classes with the same name."
          },
          {
            "type": "code",
            "src": "import subprocess, sys, tempfile, pathlib\ntmp = pathlib.Path(tempfile.mkdtemp())\n(tmp / \"registry.py\").write_text(\n    \"print(f'  running registry.py as {__name__!r}')\\n\"\n    \"items = []\\n\"\n    \"if __name__ == '__main__':\\n\"\n    \"    items.append('from main')\\n\"\n    \"    import helper\\n\"\n    \"    print('  __main__.items =', items)\\n\"\n)\n(tmp / \"helper.py\").write_text(\n    \"import registry\\n\"\n    \"print('  registry.items  =', registry.items)\\n\"\n)\nprint(subprocess.run([sys.executable, \"registry.py\"], cwd=tmp,\n                     capture_output=True, text=True).stdout.rstrip())",
            "label": null,
            "output": "  running registry.py as '__main__'\n  running registry.py as 'registry'\n  registry.items  = []\n  __main__.items = ['from main']",
            "isError": false
          },
          {
            "type": "note",
            "text": "Keep scripts thin: put logic in importable modules and make the entry point a small <code>main()</code> called under <code>if __name__ == \"__main__\":</code>, or run it with <code>python -m package.module</code>."
          }
        ]
      },
      {
        "title": "Reloading, lazy loading and module __getattr__",
        "body": [
          {
            "type": "p",
            "html": "<code>importlib.reload(mod)</code> re-executes the module's code <em>into the same module object</em>. Code that holds the module sees new values; code that copied names with <code>from mod import x</code>, and instances of the old classes, do not."
          },
          {
            "type": "code",
            "src": "import sys, tempfile, pathlib, importlib\ntmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))\nsrc = tmp / \"shapes.py\"\n\nsrc.write_text(\"class Square:\\n    sides = 4\\nRATE = 1\\n\")\nimport shapes\nfrom shapes import RATE\nold_obj = shapes.Square()\n\nsrc.write_text(\"class Square:\\n    sides = 4\\nRATE = 2\\n\")\nimportlib.invalidate_caches()\nsame = importlib.reload(shapes)\n\nprint(same is shapes, shapes.RATE, RATE)\nprint(isinstance(old_obj, shapes.Square))   # old instance, new class object",
            "label": null,
            "output": "True 2 1\nFalse",
            "isError": false
          },
          {
            "type": "p",
            "html": "Python 3.7 added module-level <code>__getattr__</code> and <code>__dir__</code> (PEP 562). They let a module compute attributes on demand &mdash; for deprecation warnings, or to defer importing a heavy submodule until someone actually uses it."
          },
          {
            "type": "code",
            "src": "import sys, tempfile, pathlib\ntmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))\n(tmp / \"toolkit\").mkdir()\n(tmp / \"toolkit\" / \"__init__.py\").write_text(\n    \"import importlib\\n\"\n    \"_LAZY = {'plotting'}\\n\"\n    \"def __getattr__(name):\\n\"\n    \"    if name in _LAZY:\\n\"\n    \"        mod = importlib.import_module(f'.{name}', __name__)\\n\"\n    \"        globals()[name] = mod          # cache: next access is a plain lookup\\n\"\n    \"        return mod\\n\"\n    \"    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')\\n\"\n)\n(tmp / \"toolkit\" / \"plotting.py\").write_text(\"print('  (expensive plotting import)')\\ndef plot(): return 'plotted'\\n\")\n\nimport toolkit\nprint(\"plotting loaded?\", \"toolkit.plotting\" in sys.modules)\nprint(toolkit.plotting.plot())\nprint(\"plotting loaded?\", \"toolkit.plotting\" in sys.modules)",
            "label": null,
            "output": "plotting loaded? False\n  (expensive plotting import)\nplotted\nplotting loaded? True",
            "isError": false
          }
        ]
      },
      {
        "title": "Import hooks: importing from anywhere",
        "body": [
          {
            "type": "p",
            "html": "Finders on <code>sys.meta_path</code> are ordinary objects with a <code>find_spec</code> method. Add your own and <code>import</code> can load modules from a database, a zip in memory, a URL or generated source. This is how pytest rewrites <code>assert</code> statements, and how tools like editable installs work."
          },
          {
            "type": "code",
            "src": "import sys, importlib.abc, importlib.util\n\nSOURCES = {\n    \"virtual_math\": \"def double(x):\\n    return 2 * x\\n\",\n    \"virtual_greet\": \"NAME = 'from a dict'\\n\",\n}\n\nclass DictFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):\n    def find_spec(self, name, path, target=None):\n        if name in SOURCES:\n            return importlib.util.spec_from_loader(name, self, origin=\"dict\")\n        return None                      # let the next finder try\n\n    def create_module(self, spec):\n        return None                      # default module object\n\n    def exec_module(self, module):\n        exec(SOURCES[module.__name__], module.__dict__)\n\nsys.meta_path.insert(0, DictFinder())\n\nimport virtual_math, virtual_greet\nprint(virtual_math.double(21), virtual_greet.NAME, virtual_math.__spec__.origin)",
            "label": null,
            "output": "42 from a dict dict",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why does a module's top-level code run only once, even if twenty files import it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "The first import puts the module object in <code>sys.modules</code>; every later <code>import</code> statement checks that dict first and just binds the cached object. Deleting the entry (<code>del sys.modules[\"m\"]</code>) makes the next import execute the file again and produce a <em>new</em> module object &mdash; while everything that imported the old one keeps it."
          },
          {
            "type": "code",
            "src": "import sys, tempfile, pathlib\ntmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))\n(tmp / \"counter.py\").write_text(\"print('  executing counter.py')\\nhits = 0\\n\")\n\nimport counter\ncounter.hits += 1\nimport counter                   # cached, still hits == 1\nfirst = counter\ndel sys.modules[\"counter\"]\nimport counter                   # executes again: a brand new module\nprint(first.hits, counter.hits, first is counter)",
            "label": null,
            "output": "  executing counter.py\n  executing counter.py\n1 0 False",
            "isError": false
          }
        ]
      },
      {
        "q": "Explain how a circular import fails with <code>ImportError: cannot import name</code> but works with <code>import module</code>.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "When <code>a</code> starts executing, it is already in <code>sys.modules</code> as an empty-ish module. If it imports <code>b</code>, and <code>b</code> does <code>from a import f</code>, the import system finds the partly built <code>a</code> in the cache and tries to read <code>a.f</code> immediately &mdash; but <code>a</code> has not reached <code>def f</code> yet, so the name lookup fails."
          },
          {
            "type": "p",
            "html": "<code>import a</code> in <code>b</code> only binds the module object, which already exists. The attribute lookup <code>a.f</code> is postponed to when <code>b</code>'s function actually runs, by which time <code>a</code> has finished executing. Same cycle, but no name is needed before it exists. The better fix is still to remove the cycle by moving shared code into a third module."
          }
        ]
      },
      {
        "q": "You changed a library file but the running program still behaves the old way. List the reasons.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<strong>sys.modules cache</strong>: the module was imported before the edit and is never re-read. Restart, or <code>importlib.reload</code> with its caveats. <strong>Stale names</strong>: even after a reload, <code>from lib import f</code> elsewhere still holds the old <code>f</code>, and existing instances keep their old class. <strong>A different copy</strong>: <code>sys.path</code> found another <code>lib</code> earlier (an installed version shadowing your editable checkout); check <code>lib.__file__</code>. <strong>Stale bytecode</strong> is rarely the cause: CPython compares the source's modification time against the <code>.pyc</code> header and recompiles."
          },
          {
            "type": "code",
            "src": "import json, importlib.util\nprint(json.__name__, \"from\", json.__spec__.origin.rsplit(\"/\", 2)[-2] + \"/\" + json.__spec__.origin.rsplit(\"/\", 1)[-1])\nprint(\"cached at:\", importlib.util.cache_from_source(\"lib.py\"))",
            "label": null,
            "output": "json from json/__init__.py\ncached at: __pycache__/lib.cpython-314.pyc",
            "isError": false
          }
        ]
      },
      {
        "q": "What is the difference between running <code>python pkg/tool.py</code> and <code>python -m pkg.tool</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>python pkg/tool.py</code> runs the file as <code>__main__</code> with no package, and puts <code>pkg/</code> (the script's directory) at the front of <code>sys.path</code>. Relative imports fail, and absolute imports of <code>pkg.something</code> only work if the project root happens to be importable."
          },
          {
            "type": "p",
            "html": "<code>python -m pkg.tool</code> imports <code>pkg</code> first (running its <code>__init__</code>), runs <code>tool</code> as <code>__main__</code> with <code>__package__ = \"pkg\"</code>, and puts the current directory on <code>sys.path</code>. Relative imports work and the module is found the same way any other code would find it. For anything inside a package, <code>-m</code> is the right way to run it."
          }
        ]
      },
      {
        "q": "How would you make <code>import heavy_lib</code> at the top of a CLI not slow down <code>--help</code>?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Options, from simplest: move the import inside the function that needs it (imports after the first are a dict lookup, so the repeated cost is negligible); use a module-level <code>__getattr__</code> in your own package to import submodules on first attribute access; or use <code>importlib.util.LazyLoader</code>, which returns a module object whose code runs on first attribute access."
          },
          {
            "type": "code",
            "src": "import sys, importlib.util\n\ndef lazy_import(name):\n    spec = importlib.util.find_spec(name)\n    loader = importlib.util.LazyLoader(spec.loader)\n    spec.loader = loader\n    module = importlib.util.module_from_spec(spec)\n    sys.modules[name] = module\n    loader.exec_module(module)          # does NOT run the module yet\n    return module\n\ndecimal = lazy_import(\"decimal\")\nprint(type(decimal).__name__)           # a lazy module proxy\nprint(decimal.Decimal(\"1.10\") + decimal.Decimal(\"2.205\"))   # first use runs it\nprint(type(decimal).__name__)",
            "label": null,
            "output": "_LazyModule\n3.305\nmodule",
            "isError": false
          },
          {
            "type": "p",
            "html": "Measure first with <code>python -X importtime -c \"import yourcli\"</code>, which prints the time spent in every import, nested."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: The import system",
        "url": "https://docs.python.org/3/reference/import.html"
      },
      {
        "label": "Python docs: importlib",
        "url": "https://docs.python.org/3/library/importlib.html"
      },
      {
        "label": "Python docs: __main__",
        "url": "https://docs.python.org/3/library/__main__.html"
      },
      {
        "label": "PEP 562: Module __getattr__ and __dir__",
        "url": "https://peps.python.org/pep-0562/"
      },
      {
        "label": "PEP 420: Implicit namespace packages",
        "url": "https://peps.python.org/pep-0420/"
      }
    ]
  },
  {
    "id": "async",
    "title": "Async Internals",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "<code>asyncio</code> runs thousands of concurrent tasks on one thread, with no locks around your data and no thread switches. There is no magic in how: a coroutine is a function that can pause, <code>await</code> is the pause point, and the event loop is an ordinary loop that resumes whichever coroutine has something to do next.",
      "This page builds the machinery up from generators, writes a toy event loop, then maps it onto the real one: tasks, futures, <code>gather</code> and <code>TaskGroup</code>, cancellation and timeouts, why one blocking call freezes everything, and how to bridge sync and async code."
    ],
    "sections": [
      {
        "title": "Concurrency on one thread",
        "body": [
          {
            "type": "p",
            "html": "Threads get concurrency by letting the OS interrupt them at any instruction (<em>pre-emptive</em>). Async code gets it by having each task voluntarily give up control at an <code>await</code> (<em>cooperative</em>). Between two <code>await</code>s your code cannot be interrupted, which is why most async code needs no locks &mdash; and why one task that never awaits stalls every other."
          },
          {
            "type": "table",
            "head": [
              "",
              "Threads",
              "asyncio"
            ],
            "rows": [
              [
                "Switching",
                "Pre-emptive, anywhere",
                "Cooperative, only at <code>await</code>"
              ],
              [
                "Parallel CPU work",
                "No (GIL)",
                "No (one thread)"
              ],
              [
                "Cost per task",
                "An OS thread: ~MBs of stack reserved, kernel scheduling",
                "A Python object: a few KB"
              ],
              [
                "Practical scale",
                "Hundreds",
                "Tens of thousands"
              ],
              [
                "Shared-state races",
                "Anywhere",
                "Only across an <code>await</code>"
              ],
              [
                "Libraries",
                "Any blocking library",
                "Must be async-aware (or offloaded to a thread)"
              ]
            ]
          }
        ]
      },
      {
        "title": "A coroutine is an object",
        "body": [
          {
            "type": "p",
            "html": "Calling an <code>async def</code> function runs none of its body. It returns a coroutine object: a paused computation. Something must drive it &mdash; normally the event loop, via <code>await</code> or a task."
          },
          {
            "type": "code",
            "src": "import asyncio, warnings\nwarnings.simplefilter(\"ignore\", RuntimeWarning)   # hide the 'never awaited' warning\n\nasync def fetch():\n    print(\"  body runs\")\n    return 42\n\nc = fetch()\nprint(type(c).__name__, \"- nothing printed yet\")\nc.close()\n\nprint(asyncio.run(fetch()))",
            "label": null,
            "output": "coroutine - nothing printed yet\n  body runs\n42",
            "isError": false
          },
          {
            "type": "p",
            "html": "Forgetting an <code>await</code> is the classic async bug: <code>fetch()</code> on its own line creates a coroutine, throws it away, and Python emits <code>RuntimeWarning: coroutine 'fetch' was never awaited</code>."
          }
        ]
      },
      {
        "title": "Under the hood: generators and send()",
        "body": [
          {
            "type": "p",
            "html": "Coroutines are built on the same machinery as generators. A generator pauses at <code>yield</code>; you resume it with <code>send()</code>; when it returns, it raises <code>StopIteration</code> carrying the return value. A coroutine is driven the same way:"
          },
          {
            "type": "code",
            "src": "import types\n\n@types.coroutine\ndef suspend(reason):\n    received = yield reason          # the one real yield in the chain\n    return received\n\nasync def child():\n    got = await suspend(\"waiting for data\")\n    return f\"child got {got!r}\"\n\nasync def parent():\n    result = await child()           # await chains through child ...\n    return result.upper()\n\ncoro = parent()\nprint(\"yielded to driver:\", coro.send(None))    # runs until the yield\ntry:\n    coro.send(\"payload\")                        # resume with a value\nexcept StopIteration as done:\n    print(\"returned:\", done.value)",
            "label": null,
            "output": "yielded to driver: waiting for data\nreturned: CHILD GOT 'PAYLOAD'",
            "isError": false
          },
          {
            "type": "p",
            "html": "This is the whole secret of <code>await</code>: it delegates down the chain (<code>parent</code> &rarr; <code>child</code> &rarr; <code>suspend</code>) until something at the bottom actually yields. That yielded value travels straight back up to whoever called <code>send</code> &mdash; the event loop. In asyncio, what is yielded at the bottom is a <code>Future</code>: &ldquo;wake me when this is done&rdquo;."
          }
        ]
      },
      {
        "title": "A toy event loop",
        "body": [
          {
            "type": "p",
            "html": "With <code>send</code> you can write an event loop in twenty lines. Each task yields how long it wants to sleep; the loop keeps a heap of wake-up times and always resumes the earliest. It uses a fake clock so the output is deterministic."
          },
          {
            "type": "code",
            "src": "import heapq, types\n\n@types.coroutine\ndef sleep(seconds):\n    yield seconds\n\nclass Loop:\n    def __init__(self):\n        self.now, self.ready, self.seq = 0.0, [], 0\n    def spawn(self, coro, at=0.0):\n        heapq.heappush(self.ready, (at, self.seq, coro)); self.seq += 1\n    def run(self):\n        while self.ready:\n            self.now, _, coro = heapq.heappop(self.ready)\n            try:\n                delay = coro.send(None)\n                self.spawn(coro, self.now + delay)\n            except StopIteration:\n                pass\n\nloop = Loop()\n\nasync def worker(name, delay, steps):\n    for i in range(steps):\n        print(f\"t={loop.now:.1f}  {name} step {i}\")\n        await sleep(delay)\n\nloop.spawn(worker(\"fast\", 0.3, 3))\nloop.spawn(worker(\"slow\", 0.5, 2))\nloop.run()",
            "label": null,
            "output": "t=0.0  fast step 0\nt=0.0  slow step 0\nt=0.3  fast step 1\nt=0.5  slow step 1\nt=0.6  fast step 2",
            "isError": false
          },
          {
            "type": "p",
            "html": "asyncio&rsquo;s loop is the same idea with real parts: a ready queue of callbacks, a heap of timers, and &mdash; instead of a fake clock &mdash; a call to <code>select</code>/<code>epoll</code>/<code>kqueue</code> that sleeps until the next timer is due <em>or</em> a socket becomes readable. That one system call is how one thread waits on thousands of connections at once."
          }
        ]
      },
      {
        "title": "Tasks and futures in asyncio",
        "body": [
          {
            "type": "p",
            "html": "<strong>Future</strong>: a placeholder for a result that will be set later. Awaiting an unfinished future suspends the awaiting coroutine until <code>set_result</code> or <code>set_exception</code> is called.<br><strong>Task</strong>: a Future subclass that drives a coroutine. <code>asyncio.create_task(coro)</code> schedules it on the loop immediately; it runs whenever the current task next yields."
          },
          {
            "type": "code",
            "src": "import asyncio\n\nasync def main():\n    loop = asyncio.get_running_loop()\n    fut = loop.create_future()\n    loop.call_later(0.01, fut.set_result, \"set by a timer callback\")\n    print(\"awaiting future...\")\n    print(await fut)\n\n    async def job(name):\n        print(f\"  {name} started\")\n        await asyncio.sleep(0)\n        print(f\"  {name} finished\")\n        return name\n\n    t = asyncio.create_task(job(\"task-1\"))\n    print(\"task created, not started yet:\", not t.done())\n    await asyncio.sleep(0)            # yield once: the task gets to start\n    print(\"back in main\")\n    print(\"result:\", await t)\n    print(\"is a Future:\", isinstance(t, asyncio.Future))\n\nasyncio.run(main())",
            "label": null,
            "output": "awaiting future...\nset by a timer callback\ntask created, not started yet: True\n  task-1 started\nback in main\n  task-1 finished\nresult: task-1\nis a Future: True",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Object",
              "What it is",
              "You create it with"
            ],
            "rows": [
              [
                "Coroutine",
                "A paused function body; does nothing until driven",
                "Calling an <code>async def</code> function"
              ],
              [
                "Future",
                "A result slot plus a list of callbacks to run when it is filled",
                "<code>loop.create_future()</code> (rarely by hand)"
              ],
              [
                "Task",
                "A Future that runs a coroutine to completion on the loop",
                "<code>asyncio.create_task()</code>, <code>TaskGroup.create_task()</code>"
              ]
            ]
          }
        ]
      },
      {
        "title": "Sequential await vs concurrent tasks",
        "body": [
          {
            "type": "p",
            "html": "<code>await</code> on a coroutine runs it to completion before moving on. For concurrency you must create tasks &mdash; directly, or through <code>gather</code> or a <code>TaskGroup</code>."
          },
          {
            "type": "code",
            "src": "import asyncio, time\n\nasync def io(name, seconds):\n    await asyncio.sleep(seconds)\n    return name\n\nasync def main():\n    start = time.perf_counter()\n    a = await io(\"a\", 0.2)\n    b = await io(\"b\", 0.2)\n    c = await io(\"c\", 0.2)\n    print(f\"sequential: {time.perf_counter() - start:.1f}s\", [a, b, c])\n\n    start = time.perf_counter()\n    results = await asyncio.gather(io(\"a\", 0.2), io(\"b\", 0.2), io(\"c\", 0.2))\n    print(f\"gather:     {time.perf_counter() - start:.1f}s\", results)\n\n    start = time.perf_counter()\n    async with asyncio.TaskGroup() as tg:\n        tasks = [tg.create_task(io(n, 0.2)) for n in \"abc\"]\n    print(f\"TaskGroup:  {time.perf_counter() - start:.1f}s\", [t.result() for t in tasks])\n\nasyncio.run(main())",
            "label": null,
            "output": "sequential: 0.6s ['a', 'b', 'c']\ngather:     0.2s ['a', 'b', 'c']\nTaskGroup:  0.2s ['a', 'b', 'c']",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>TaskGroup</code> (3.11+) is <em>structured concurrency</em>: no task can outlive the <code>async with</code> block, and if one task fails, the others are cancelled and all errors are raised together as an <code>ExceptionGroup</code>. Prefer it to bare <code>create_task</code> and to <code>gather</code> in new code."
          }
        ]
      },
      {
        "title": "Never block the event loop",
        "body": [
          {
            "type": "p",
            "html": "The loop can only switch tasks at an <code>await</code>. A blocking call &mdash; <code>time.sleep</code>, <code>requests.get</code>, a heavy computation, a sync database driver &mdash; holds the only thread, and every other task freezes until it returns."
          },
          {
            "type": "code",
            "src": "import asyncio, time\n\nasync def heartbeat(log):\n    for _ in range(3):\n        log.append(\"beat\")\n        await asyncio.sleep(0.05)\n\nasync def bad_worker(log):\n    time.sleep(0.2)                         # blocks the whole loop\n    log.append(\"bad done\")\n\nasync def good_worker(log):\n    await asyncio.to_thread(time.sleep, 0.2)   # blocks a worker thread instead\n    log.append(\"good done\")\n\nasync def run(worker):\n    log = []\n    await asyncio.gather(worker(log), heartbeat(log))\n    return log\n\nprint(\"blocking:  \", asyncio.run(run(bad_worker)))\nprint(\"to_thread: \", asyncio.run(run(good_worker)))",
            "label": null,
            "output": "blocking:   ['bad done', 'beat', 'beat', 'beat']\nto_thread:  ['beat', 'beat', 'beat', 'good done']",
            "isError": false
          },
          {
            "type": "p",
            "html": "With the blocking call, the worker was scheduled first and held the only thread for the full 0.2&nbsp;s, so the heartbeat could not even start until it had finished. With <code>to_thread</code>, the wait happens on a thread pool, the heartbeat beats three times while the worker waits, and the worker finishes last. For CPU-heavy work use <code>loop.run_in_executor</code> with a <code>ProcessPoolExecutor</code>, since a thread would still hold the GIL."
          },
          {
            "type": "note",
            "text": "Turn on debug mode (<code>asyncio.run(main(), debug=True)</code> or <code>PYTHONASYNCIODEBUG=1</code>) in development: it logs every callback that blocks the loop for more than 100&nbsp;ms, and names coroutines that were never awaited."
          }
        ]
      },
      {
        "title": "Cancellation and timeouts",
        "body": [
          {
            "type": "p",
            "html": "Cancelling a task throws <code>CancelledError</code> into it at its current <code>await</code>. The task can run cleanup in <code>finally</code>, but should let the error propagate &mdash; swallowing it breaks timeouts and <code>TaskGroup</code>."
          },
          {
            "type": "code",
            "src": "import asyncio\n\nasync def download():\n    try:\n        print(\"  downloading...\")\n        await asyncio.sleep(10)\n    except asyncio.CancelledError:\n        print(\"  cancelled: cleaning up partial file\")\n        raise                                   # always re-raise\n    finally:\n        print(\"  finally runs\")\n\nasync def main():\n    t = asyncio.create_task(download())\n    await asyncio.sleep(0.01)\n    t.cancel()\n    try:\n        await t\n    except asyncio.CancelledError:\n        print(\"task cancelled:\", t.cancelled())\n\n    try:\n        async with asyncio.timeout(0.05):\n            await download()\n    except TimeoutError:\n        print(\"timed out -> TimeoutError\")\n\nasyncio.run(main())",
            "label": null,
            "output": "  downloading...\n  cancelled: cleaning up partial file\n  finally runs\ntask cancelled: True\n  downloading...\n  cancelled: cleaning up partial file\n  finally runs\ntimed out -> TimeoutError",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>asyncio.timeout</code> (3.11+) cancels the work inside it and converts the <code>CancelledError</code> into a <code>TimeoutError</code> at the block boundary. <code>asyncio.wait_for(coro, t)</code> is the older, function-style equivalent."
          },
          {
            "type": "caveat",
            "text": "A few operations are not cancellable at all: code running in <code>to_thread</code> keeps running in its thread after the awaiting task is cancelled. Use <code>asyncio.shield</code> to protect an inner operation from an outer cancellation when it must finish."
          }
        ]
      },
      {
        "title": "Limiting concurrency and passing work between tasks",
        "body": [
          {
            "type": "p",
            "html": "Launching 10,000 requests at once will exhaust sockets or get you rate-limited. An <code>asyncio.Semaphore</code> caps how many are in flight; an <code>asyncio.Queue</code> connects producers and consumers with back-pressure."
          },
          {
            "type": "code",
            "src": "import asyncio\n\nasync def main():\n    limit = asyncio.Semaphore(3)\n    active, peak = 0, 0\n\n    async def fetch(i):\n        nonlocal active, peak\n        async with limit:\n            active += 1\n            peak = max(peak, active)\n            await asyncio.sleep(0.01)\n            active -= 1\n            return i * i\n\n    results = await asyncio.gather(*(fetch(i) for i in range(20)))\n    print(\"results ok:\", results == [i * i for i in range(20)])\n    print(\"never more than 3 at once:\", peak)\n\n    queue = asyncio.Queue(maxsize=2)\n    async def producer():\n        for i in range(5):\n            await queue.put(i)          # waits while the queue is full\n        await queue.put(None)\n    async def consumer():\n        seen = []\n        while (item := await queue.get()) is not None:\n            seen.append(item)\n        return seen\n    _, seen = await asyncio.gather(producer(), consumer())\n    print(\"consumed:\", seen)\n\nasyncio.run(main())",
            "label": null,
            "output": "results ok: True\nnever more than 3 at once: 3\nconsumed: [0, 1, 2, 3, 4]",
            "isError": false
          },
          {
            "type": "p",
            "html": "No lock was needed around <code>active</code> and <code>peak</code>: each read-modify-write happens between two <code>await</code>s, so no other task can interleave. Add an <code>await</code> in the middle of such an update and you would need an <code>asyncio.Lock</code>."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What is the difference between a coroutine, a Task and a Future?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A <strong>coroutine</strong> is the paused function body produced by calling an <code>async def</code> function. Nothing runs until something drives it. A <strong>Future</strong> is a low-level result container with callbacks, awaitable, and completed by someone calling <code>set_result</code>. A <strong>Task</strong> is a Future that owns a coroutine and drives it on the event loop, completing with the coroutine&rsquo;s return value."
          },
          {
            "type": "p",
            "html": "Consequence: <code>await coro()</code> runs the coroutine inline, in the current task, one after another. <code>create_task(coro())</code> starts it running concurrently and gives you a handle to await, cancel or inspect later. Keep a reference to tasks you create &mdash; the loop only holds a weak reference, so a fire-and-forget task with no other reference can be garbage-collected mid-flight."
          }
        ]
      },
      {
        "q": "What happens if you call <code>time.sleep(5)</code> or <code>requests.get()</code> inside an <code>async def</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "The whole event loop stops for those five seconds. The loop runs on one thread and can only switch tasks at an <code>await</code>; a blocking call never yields, so every other task &mdash; every other client connection on a server &mdash; waits. Nothing crashes, which is why it is easy to ship: the symptom is latency spikes under load."
          },
          {
            "type": "p",
            "html": "Fixes, in order of preference: use the async equivalent (<code>await asyncio.sleep</code>, <code>httpx.AsyncClient</code>, an async DB driver); otherwise offload with <code>await asyncio.to_thread(blocking_fn, ...)</code>; for CPU-bound work, <code>loop.run_in_executor(process_pool, fn, ...)</code>."
          }
        ]
      },
      {
        "q": "Fetch 1,000 URLs concurrently, but never more than 20 at a time, and collect failures without stopping the rest.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "A semaphore for the cap; <code>gather(..., return_exceptions=True)</code> so one failure does not cancel the others; then split results from errors. Here the network call is simulated so the answer is runnable."
          },
          {
            "type": "code",
            "src": "import asyncio\n\nasync def fake_get(url):\n    await asyncio.sleep(0.001)\n    if url.endswith(\"7\"):\n        raise ConnectionError(f\"{url} unreachable\")\n    return f\"<html {url}>\"\n\nasync def fetch_all(urls, limit=20):\n    sem = asyncio.Semaphore(limit)\n    async def one(url):\n        async with sem:\n            return url, await fake_get(url)\n    results = await asyncio.gather(*(one(u) for u in urls), return_exceptions=True)\n    ok = dict(r for r in results if not isinstance(r, BaseException))\n    failed = [r for r in results if isinstance(r, BaseException)]\n    return ok, failed\n\nurls = [f\"https://example.com/{i}\" for i in range(1000)]\nok, failed = asyncio.run(fetch_all(urls))\nprint(len(ok), \"succeeded,\", len(failed), \"failed\")\nprint(failed[0])",
            "label": null,
            "output": "900 succeeded, 100 failed\nhttps://example.com/7 unreachable",
            "isError": false
          },
          {
            "type": "p",
            "html": "Points interviewers look for: creating one client session and reusing it (connection pooling), a per-request timeout (<code>asyncio.timeout</code>) so one hung server cannot hold a semaphore slot forever, retries with back-off for transient errors, and &mdash; for truly huge lists &mdash; a fixed pool of worker tasks reading from a <code>Queue</code> instead of creating a million coroutine objects up front."
          }
        ]
      },
      {
        "q": "How do <code>gather</code> and <code>TaskGroup</code> behave differently when one task fails?",
        "level": "hard",
        "answer": [
          {
            "type": "code",
            "src": "import asyncio\n\nasync def ok(name, delay):\n    try:\n        await asyncio.sleep(delay)\n        return name\n    except asyncio.CancelledError:\n        print(f\"  {name} was cancelled\")\n        raise\n\nasync def boom():\n    await asyncio.sleep(0.01)\n    raise ValueError(\"boom\")\n\nasync def main():\n    print(\"gather:\")\n    slow = asyncio.create_task(ok(\"slow\", 0.05))\n    try:\n        await asyncio.gather(slow, boom())\n    except ValueError as e:\n        print(\"  raised\", repr(e), \"| slow still running:\", not slow.done())\n    print(\"  slow finished anyway:\", await slow)\n\n    print(\"TaskGroup:\")\n    try:\n        async with asyncio.TaskGroup() as tg:\n            tg.create_task(ok(\"slow\", 0.05))\n            tg.create_task(boom())\n    except* ValueError as eg:\n        print(\"  raised\", repr(eg.exceptions))\n\nasyncio.run(main())",
            "label": null,
            "output": "gather:\n  raised ValueError('boom') | slow still running: True\n  slow finished anyway: slow\nTaskGroup:\n  slow was cancelled\n  raised (ValueError('boom'),)",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>gather</code> (without <code>return_exceptions</code>) propagates the first exception to the awaiting code immediately, but does <em>not</em> cancel the other tasks &mdash; they keep running unobserved, which is how leaked background work happens. <code>TaskGroup</code> cancels the siblings, waits for them to finish, and raises every failure together in an <code>ExceptionGroup</code>, which you handle with <code>except*</code>."
          }
        ]
      },
      {
        "q": "How does <code>await</code> actually suspend a function and get it resumed later?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "A coroutine is a generator-like frame. <code>await x</code> calls <code>x.__await__()</code> to get an iterator and delegates to it, like <code>yield from</code>. The chain continues down until a <code>Future</code>&rsquo;s <code>__await__</code> hits a real <code>yield self</code>. That yield unwinds straight up to the Task, which called <code>coro.send(None)</code>."
          },
          {
            "type": "p",
            "html": "The Task sees it received a Future, registers its own <code>__step</code> method as a done-callback on that future, and returns to the event loop. The coroutine&rsquo;s frame is simply left suspended in memory. Later, when an I/O event or timer completes the future, its callbacks are scheduled; the Task&rsquo;s <code>__step</code> runs, calls <code>coro.send(None)</code> again, and execution resumes exactly after the <code>yield</code> &mdash; inside the <code>await</code> expression, which now returns the future&rsquo;s result."
          },
          {
            "type": "code",
            "src": "import asyncio\n\nclass Ticket:\n    \"\"\"A minimal awaitable: yields a Future to the Task, returns its result.\"\"\"\n    def __init__(self, fut): self.fut = fut\n    def __await__(self):\n        print(\"  __await__: yielding the future to the Task\")\n        result = yield from self.fut.__await__()\n        print(\"  __await__: resumed with\", repr(result))\n        return result\n\nasync def main():\n    loop = asyncio.get_running_loop()\n    fut = loop.create_future()\n    loop.call_soon(fut.set_result, \"ready\")\n    print(\"value:\", await Ticket(fut))\n\nasyncio.run(main())",
            "label": null,
            "output": "  __await__: yielding the future to the Task\n  __await__: resumed with 'ready'\nvalue: ready",
            "isError": false
          }
        ]
      },
      {
        "q": "How do you call async code from sync code, and sync code from async code?",
        "level": "medium",
        "answer": [
          {
            "type": "table",
            "head": [
              "From",
              "To",
              "Use"
            ],
            "rows": [
              [
                "Sync (top level)",
                "Async",
                "<code>asyncio.run(main())</code> &mdash; creates a loop, runs, closes it. Once per program, not in a loop"
              ],
              [
                "Sync code in another thread",
                "Async on a running loop",
                "<code>asyncio.run_coroutine_threadsafe(coro, loop).result()</code>"
              ],
              [
                "Async",
                "Blocking sync function",
                "<code>await asyncio.to_thread(fn, *args)</code>"
              ],
              [
                "Async",
                "CPU-heavy sync function",
                "<code>await loop.run_in_executor(process_pool, fn, *args)</code>"
              ],
              [
                "Async",
                "Quick, non-blocking sync function",
                "Just call it"
              ]
            ]
          },
          {
            "type": "code",
            "src": "import asyncio, threading\n\nasync def double(x):\n    await asyncio.sleep(0)\n    return x * 2\n\nasync def main():\n    loop = asyncio.get_running_loop()\n    out = []\n\n    def sync_worker():                       # runs in a plain thread\n        fut = asyncio.run_coroutine_threadsafe(double(21), loop)\n        out.append(fut.result())\n\n    t = threading.Thread(target=sync_worker)\n    t.start()\n    await asyncio.to_thread(t.join)          # do not block the loop while waiting\n    print(\"thread got:\", out[0])\n\nprint(asyncio.run(double(5)))\nasyncio.run(main())",
            "label": null,
            "output": "10\nthread got: 42",
            "isError": false
          },
          {
            "type": "p",
            "html": "What does not work: calling <code>asyncio.run</code> from inside a running loop (it raises <code>RuntimeError</code>), or calling <code>fut.result()</code> on the loop&rsquo;s own thread, which deadlocks."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: asyncio",
        "url": "https://docs.python.org/3/library/asyncio.html"
      },
      {
        "label": "PEP 492 — Coroutines with async and await syntax",
        "url": "https://peps.python.org/pep-0492/"
      },
      {
        "label": "Python docs: Developing with asyncio",
        "url": "https://docs.python.org/3/library/asyncio-dev.html"
      },
      {
        "label": "Python docs: TaskGroup",
        "url": "https://docs.python.org/3/library/asyncio-task.html#task-groups"
      }
    ]
  },
  {
    "id": "asyncio-pitfalls",
    "title": "asyncio Pitfalls",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "",
    "intro": [
      "The async internals topic explains how the event loop and coroutines work. This one is about how async code goes wrong in practice. Almost every bug has the same root: <strong>an event loop is one thread running one task at a time, and a task only gives up control at an <code>await</code></strong>. Forget that, and you get code that blocks every other request, loses exceptions, races on shared state, or never runs at all.",
      "Each section shows the bug running, then the fix. The interview versions of these questions are &ldquo;why is my async server slow&rdquo; and &ldquo;where did my exception go&rdquo;."
    ],
    "sections": [
      {
        "title": "Forgetting await",
        "body": [
          {
            "type": "p",
            "html": "Calling a coroutine function does not run it. It creates a coroutine object, which does nothing until it is awaited or wrapped in a task. Forget the <code>await</code> and the work silently never happens; the only clue is a <code>RuntimeWarning</code> when the unused coroutine is garbage-collected."
          },
          {
            "type": "code",
            "src": "import asyncio, sys, warnings\nsys.stderr = sys.stdout                   # show the warning inline\nwarnings.simplefilter(\"always\")\n\nsaved = []\n\nasync def save(item):\n    await asyncio.sleep(0)\n    saved.append(item)\n\nasync def main():\n    save(\"a\")                             # BUG: creates a coroutine, never runs it\n    await save(\"b\")\n    print(\"saved:\", saved)\n\nasyncio.run(main())",
            "label": null,
            "output": "asyncio_pitfalls_s0_1.py:12: RuntimeWarning: coroutine 'save' was never awaited\n  save(\"a\")                             # BUG: creates a coroutine, never runs it\nRuntimeWarning: Enable tracemalloc to get the object allocation traceback\nsaved: ['b']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Turn on debug mode (<code>PYTHONASYNCIODEBUG=1</code> or <code>asyncio.run(main(), debug=True)</code>) in development, and use a linter: both catch this and several of the problems below. Type checkers flag an unused coroutine result too."
          }
        ]
      },
      {
        "title": "Blocking the event loop",
        "body": [
          {
            "type": "p",
            "html": "While a coroutine runs code that does not <code>await</code> &mdash; <code>time.sleep</code>, <code>requests.get</code>, a big JSON parse, a CPU loop &mdash; nothing else on the loop can run. Ten concurrent requests become ten sequential ones."
          },
          {
            "type": "code",
            "src": "import asyncio, time\n\nasync def handler_blocking(i):\n    time.sleep(0.2)                       # blocks the whole loop\n    return i\n\nasync def handler_async(i):\n    await asyncio.sleep(0.2)              # yields to the loop while waiting\n    return i\n\nasync def timed(handler):\n    start = time.perf_counter()\n    await asyncio.gather(*(handler(i) for i in range(5)))\n    return round(time.perf_counter() - start, 1)\n\nprint(\"time.sleep    :\", asyncio.run(timed(handler_blocking)), \"s\")\nprint(\"asyncio.sleep :\", asyncio.run(timed(handler_async)), \"s\")",
            "label": null,
            "output": "time.sleep    : 1.0 s\nasyncio.sleep : 0.2 s",
            "isError": false
          },
          {
            "type": "p",
            "html": "When you must call blocking code (a library with no async version, file I/O, a C extension), move it to a thread with <code>asyncio.to_thread</code>. The loop keeps running while the thread waits. For CPU-bound work, threads do not help under the GIL; use a <code>ProcessPoolExecutor</code> with <code>loop.run_in_executor</code>."
          },
          {
            "type": "code",
            "src": "import asyncio, time\n\ndef legacy_fetch(i):                      # a blocking library call\n    time.sleep(0.2)\n    return f\"result-{i}\"\n\nasync def main():\n    start = time.perf_counter()\n    results = await asyncio.gather(*(asyncio.to_thread(legacy_fetch, i) for i in range(5)))\n    print(results)\n    print(\"elapsed\", round(time.perf_counter() - start, 1), \"s\")\n\nasyncio.run(main())",
            "label": null,
            "output": "['result-0', 'result-1', 'result-2', 'result-3', 'result-4']\nelapsed 0.2 s",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Work",
              "Inside async code, use"
            ],
            "rows": [
              [
                "Waiting on network or timers",
                "An async library (<code>aiohttp</code>, <code>httpx.AsyncClient</code>, <code>asyncpg</code>) and <code>await</code>"
              ],
              [
                "A blocking call you cannot replace",
                "<code>await asyncio.to_thread(fn, *args)</code>"
              ],
              [
                "CPU-heavy computation",
                "<code>await loop.run_in_executor(process_pool, fn, *args)</code>"
              ],
              [
                "A tight loop over many items",
                "<code>await asyncio.sleep(0)</code> every so often to let others run"
              ]
            ]
          }
        ]
      },
      {
        "title": "Fire-and-forget tasks and lost exceptions",
        "body": [
          {
            "type": "p",
            "html": "<code>asyncio.create_task</code> schedules a coroutine and returns a <code>Task</code>. The event loop keeps only a <em>weak</em> reference to it, so a task nobody holds can be garbage-collected mid-flight. And if a task raises and nobody awaits it, the exception is not raised anywhere &mdash; it is logged as &ldquo;Task exception was never retrieved&rdquo;, if you are lucky, when the task is destroyed."
          },
          {
            "type": "code",
            "src": "import asyncio, sys\nsys.stderr = sys.stdout\n\nasync def send_email(to):\n    await asyncio.sleep(0.01)\n    raise ConnectionError(f\"SMTP down, could not mail {to}\")\n\nasync def main():\n    asyncio.create_task(send_email(\"ann\"))   # nobody keeps it, nobody awaits it\n    await asyncio.sleep(0.05)\n    print(\"request handled, user told 'email sent'\")\n\nasyncio.run(main())\nprint(\"program finished without raising\")",
            "label": null,
            "output": "Task exception was never retrieved\nfuture: <Task finished name='Task-2' coro=<send_email() done, defined at asyncio_pitfalls_s2_1.py:4> exception=ConnectionError('SMTP down, could not mail ann')>\nTraceback (most recent call last):\n  File \"asyncio_pitfalls_s2_1.py\", line 6, in send_email\n    raise ConnectionError(f\"SMTP down, could not mail {to}\")\nConnectionError: SMTP down, could not mail ann\nrequest handled, user told 'email sent'\nprogram finished without raising",
            "isError": false
          },
          {
            "type": "p",
            "html": "The fix is to keep a strong reference and to observe the result. A set plus <code>add_done_callback</code> is the pattern the asyncio docs recommend for background tasks:"
          },
          {
            "type": "code",
            "src": "import asyncio\n\nbackground = set()\n\ndef spawn(coro):\n    task = asyncio.create_task(coro)\n    background.add(task)                      # strong reference\n    task.add_done_callback(on_done)\n    return task\n\ndef on_done(task):\n    background.discard(task)\n    if not task.cancelled() and task.exception():\n        print(f\"background task failed: {task.exception()!r}\")\n\nasync def send_email(to):\n    await asyncio.sleep(0.01)\n    raise ConnectionError(f\"SMTP down, could not mail {to}\")\n\nasync def main():\n    spawn(send_email(\"ann\"))\n    await asyncio.sleep(0.05)\n    print(\"pending tasks:\", len(background))\n\nasyncio.run(main())",
            "label": null,
            "output": "background task failed: ConnectionError('SMTP down, could not mail ann')\npending tasks: 0",
            "isError": false
          }
        ]
      },
      {
        "title": "gather vs TaskGroup",
        "body": [
          {
            "type": "p",
            "html": "<code>asyncio.gather(*aws)</code> runs awaitables concurrently and returns their results in order. If one raises, gather raises that exception to you immediately &mdash; but the <em>other</em> tasks keep running in the background, unsupervised. <code>asyncio.TaskGroup</code> (3.11+) is structured concurrency: if any task fails, the group cancels the rest, waits for them, and raises all failures together as an <code>ExceptionGroup</code>."
          },
          {
            "type": "code",
            "src": "import asyncio\n\nlog = []\n\nasync def job(name, delay, fail=False):\n    try:\n        await asyncio.sleep(delay)\n        if fail:\n            raise ValueError(f\"{name} failed\")\n        log.append(f\"{name} done\")\n    except asyncio.CancelledError:\n        log.append(f\"{name} cancelled\")\n        raise\n\nasync def with_gather():\n    try:\n        await asyncio.gather(job(\"a\", 0.01, fail=True), job(\"b\", 0.05))\n    except ValueError as e:\n        log.append(f\"caught {e}\")\n    await asyncio.sleep(0.1)                  # b is still running...\n\nasync def with_taskgroup():\n    try:\n        async with asyncio.TaskGroup() as tg:\n            tg.create_task(job(\"a\", 0.01, fail=True))\n            tg.create_task(job(\"b\", 0.05))\n    except* ValueError as eg:\n        log.append(f\"caught {[str(e) for e in eg.exceptions]}\")\n\nfor scenario in (with_gather, with_taskgroup):\n    log.clear()\n    asyncio.run(scenario())\n    print(f\"{scenario.__name__:15}\", log)",
            "label": null,
            "output": "with_gather     ['caught a failed', 'b done']\nwith_taskgroup  ['b cancelled', \"caught ['a failed']\"]",
            "isError": false
          },
          {
            "type": "p",
            "html": "With gather, <code>b</code> finished after the error was already handled &mdash; in a real server, still holding a connection or writing to a closed resource. With the TaskGroup, <code>b</code> was cancelled before the <code>async with</code> exited. <code>gather(..., return_exceptions=True)</code> is the other option when you want every result, failures included, as values."
          },
          {
            "type": "note",
            "text": "Prefer <code>TaskGroup</code> for &ldquo;run these together, and they all succeed or none do&rdquo;. Use <code>gather(return_exceptions=True)</code> for &ldquo;run all of these and tell me how each one went&rdquo;."
          }
        ]
      },
      {
        "title": "Swallowing cancellation",
        "body": [
          {
            "type": "p",
            "html": "Cancelling a task throws <code>CancelledError</code> into it at its current <code>await</code>. Since 3.8 <code>CancelledError</code> derives from <code>BaseException</code>, so <code>except Exception</code> does not catch it &mdash; but a bare <code>except:</code> or <code>except BaseException</code> does, and if the handler does not re-raise, the task carries on as if nothing happened. Timeouts and TaskGroups stop working."
          },
          {
            "type": "code",
            "src": "import asyncio\n\nasync def stubborn():\n    for i in range(3):\n        try:\n            await asyncio.sleep(0.05)\n        except BaseException:              # BUG: eats CancelledError\n            print(f\"  swallowed cancellation on step {i}\")\n    return \"finished anyway\"\n\nasync def polite():\n    try:\n        await asyncio.sleep(0.05)\n    except asyncio.CancelledError:\n        print(\"  cleaning up, then re-raising\")\n        raise\n    return \"finished\"\n\nasync def main():\n    for fn in (stubborn, polite):\n        try:\n            async with asyncio.timeout(0.01):\n                print(fn.__name__, \"->\", await fn())\n        except TimeoutError:\n            print(fn.__name__, \"-> TimeoutError (cancellation worked)\")\n\nasyncio.run(main())",
            "label": null,
            "output": "  swallowed cancellation on step 0\nstubborn -> finished anyway\n  cleaning up, then re-raising\npolite -> TimeoutError (cancellation worked)",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>stubborn</code> blew through its 10 ms timeout and ran all three steps. Rule: if you catch <code>CancelledError</code> to clean up, re-raise it. Use <code>try/finally</code> when all you need is cleanup. If a piece of work must not be interrupted, wrap it in <code>asyncio.shield</code> and accept that the caller may stop waiting for it."
          }
        ]
      },
      {
        "title": "Race conditions across await",
        "body": [
          {
            "type": "p",
            "html": "Async code has no preemption, so a block with no <code>await</code> in it is atomic. But every <code>await</code> is a point where other tasks run, and a check-then-act sequence that spans one is a race &mdash; exactly as with threads."
          },
          {
            "type": "code",
            "src": "import asyncio\n\nclass Account:\n    def __init__(self, balance):\n        self.balance = balance\n        self.lock = asyncio.Lock()\n\n    async def withdraw_racy(self, amount):\n        if self.balance >= amount:          # check\n            await asyncio.sleep(0)          # e.g. an audit-log call\n            self.balance -= amount          # act: the check may be stale\n            return True\n        return False\n\n    async def withdraw_safe(self, amount):\n        async with self.lock:               # check and act under one lock\n            if self.balance >= amount:\n                await asyncio.sleep(0)\n                self.balance -= amount\n                return True\n            return False\n\nasync def main():\n    for method in (\"withdraw_racy\", \"withdraw_safe\"):\n        acct = Account(100)\n        ok = await asyncio.gather(*(getattr(acct, method)(80) for _ in range(3)))\n        print(f\"{method:14} approved={ok.count(True)} balance={acct.balance}\")\n\nasyncio.run(main())",
            "label": null,
            "output": "withdraw_racy  approved=3 balance=-140\nwithdraw_safe  approved=1 balance=20",
            "isError": false
          },
          {
            "type": "p",
            "html": "All three racy withdrawals passed the check before any of them reached the subtraction. An <code>asyncio.Lock</code> is cheap; it does not block the thread, it only makes other tasks that want the same lock wait their turn."
          },
          {
            "type": "caveat",
            "text": "<code>asyncio.Lock</code> protects against other <em>tasks</em> on the same loop. It is not thread-safe. State shared with threads (from <code>to_thread</code> or executors) needs <code>threading.Lock</code> or, better, no sharing."
          }
        ]
      },
      {
        "title": "Unbounded concurrency",
        "body": [
          {
            "type": "p",
            "html": "<code>gather</code> over 10,000 URLs starts 10,000 requests at once: sockets run out, the remote server rate-limits you, memory spikes. Bound concurrency with a <code>Semaphore</code>, or use a fixed pool of worker tasks reading from a bounded <code>asyncio.Queue</code>, which also gives backpressure: producers wait when the queue is full."
          },
          {
            "type": "code",
            "src": "import asyncio\n\nin_flight = peak = 0\n\nasync def fetch(i, limit):\n    global in_flight, peak\n    async with limit:\n        in_flight += 1\n        peak = max(peak, in_flight)\n        await asyncio.sleep(0.01)\n        in_flight -= 1\n        return i\n\nasync def main():\n    global peak\n    for size in (1000, 20):\n        peak = 0\n        limit = asyncio.Semaphore(size)\n        results = await asyncio.gather(*(fetch(i, limit) for i in range(200)))\n        print(f\"semaphore({size:4}): {len(results)} done, peak concurrency {peak}\")\n\nasyncio.run(main())",
            "label": null,
            "output": "semaphore(1000): 200 done, peak concurrency 200\nsemaphore(  20): 200 done, peak concurrency 20",
            "isError": false
          },
          {
            "type": "code",
            "src": "import asyncio\n\nasync def producer(queue, n):\n    for i in range(n):\n        await queue.put(i)                 # waits while the queue is full\n    for _ in range(WORKERS):\n        await queue.put(None)              # one stop signal per worker\n\nasync def worker(name, queue, done):\n    while (item := await queue.get()) is not None:\n        await asyncio.sleep(0.001)\n        done.append(item)\n\nWORKERS = 4\n\nasync def main():\n    queue, done = asyncio.Queue(maxsize=10), []\n    async with asyncio.TaskGroup() as tg:\n        tg.create_task(producer(queue, 100))\n        for w in range(WORKERS):\n            tg.create_task(worker(w, queue, done))\n    print(len(done), sorted(done) == list(range(100)))\n\nasyncio.run(main())",
            "label": "worker pool with a bounded queue",
            "output": "100 True",
            "isError": false
          }
        ]
      },
      {
        "title": "Loops, threads and asyncio.run",
        "body": [
          {
            "type": "p",
            "html": "<code>asyncio.run</code> creates a new event loop, runs one coroutine, and closes the loop. It cannot be called from code that is already running inside a loop (a Jupyter cell, an async web handler). From async code, just <code>await</code>. From another <em>thread</em> that needs to submit work to a running loop, use <code>asyncio.run_coroutine_threadsafe</code>; nothing else on a loop is thread-safe."
          },
          {
            "type": "code",
            "src": "import asyncio, threading\n\nasync def compute(x):\n    await asyncio.sleep(0.01)\n    return x * 2\n\nasync def main():\n    coro = compute(1)\n    try:\n        asyncio.run(coro)\n    except RuntimeError as e:\n        coro.close()                      # never started: discard it quietly\n        print(\"RuntimeError:\", e)\n\n    loop = asyncio.get_running_loop()\n    results = []\n\n    def from_thread():\n        fut = asyncio.run_coroutine_threadsafe(compute(21), loop)\n        results.append(fut.result(timeout=1))   # blocks this thread, not the loop\n\n    t = threading.Thread(target=from_thread)\n    t.start()\n    await asyncio.to_thread(t.join)\n    print(\"from thread:\", results)\n\nasyncio.run(main())",
            "label": null,
            "output": "RuntimeError: asyncio.run() cannot be called from a running event loop\nfrom thread: [42]",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "An async web service handles one request at a time even though every handler is <code>async def</code>. What do you look for?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Something in the request path blocks the event loop. Usual suspects: a synchronous HTTP client (<code>requests</code>), a synchronous database driver, <code>time.sleep</code>, file I/O, heavy JSON or template rendering, password hashing, or any long CPU loop. <code>async def</code> only makes a function <em>able</em> to yield; it yields only at an <code>await</code> on something that actually waits asynchronously."
          },
          {
            "type": "p",
            "html": "To find it: run with <code>asyncio.run(..., debug=True)</code> (or <code>PYTHONASYNCIODEBUG=1</code>), which logs every callback that holds the loop for longer than <code>loop.slow_callback_duration</code> (100 ms by default). Fix with an async library, <code>asyncio.to_thread</code> for blocking I/O, or a process pool for CPU work."
          }
        ]
      },
      {
        "q": "What is printed, and why is the second call so different?",
        "level": "medium",
        "answer": [
          {
            "type": "code",
            "src": "import asyncio, time\n\nasync def work(n):\n    await asyncio.sleep(0.1)\n    return n\n\nasync def sequential():\n    return [await work(i) for i in range(5)]\n\nasync def concurrent():\n    return await asyncio.gather(*(work(i) for i in range(5)))\n\nfor fn in (sequential, concurrent):\n    t = time.perf_counter()\n    result = asyncio.run(fn())\n    print(f\"{fn.__name__:10} {result} {round(time.perf_counter() - t, 1)}s\")",
            "label": null,
            "output": "sequential [0, 1, 2, 3, 4] 0.5s\nconcurrent [0, 1, 2, 3, 4] 0.1s",
            "isError": false
          },
          {
            "type": "p",
            "html": "Awaiting coroutines one after another runs them one after another: <code>await</code> means &ldquo;wait for this to finish before continuing&rdquo;. Concurrency only happens when several tasks exist at the same time &mdash; <code>gather</code> wraps each coroutine in a task, so all five sleeps overlap."
          }
        ]
      },
      {
        "q": "Why can <code>asyncio.create_task(coro())</code> without keeping the result lose work?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The event loop holds tasks only through weak references. A task that nothing else references can be garbage-collected before it finishes &mdash; the coroutine just stops. Even if it survives, an exception in it is never re-raised anywhere; it is only logged when the task object is destroyed. Keep tasks in a collection (or a <code>TaskGroup</code>), remove them in a done-callback, and check <code>task.exception()</code> there. In 3.12+ <code>asyncio.TaskGroup</code> or a framework-provided background-task API is the cleaner choice."
          }
        ]
      },
      {
        "q": "Write a function that runs coroutines with at most N in flight and returns results in input order.",
        "level": "medium",
        "answer": [
          {
            "type": "code",
            "src": "import asyncio, random\n\nasync def bounded_gather(coros, limit):\n    sem = asyncio.Semaphore(limit)\n    active = peak = 0\n\n    async def run(coro):\n        nonlocal active, peak\n        async with sem:\n            active += 1\n            peak = max(peak, active)\n            try:\n                return await coro\n            finally:\n                active -= 1\n\n    results = await asyncio.gather(*(run(c) for c in coros))\n    return results, peak\n\nasync def fetch(i):\n    await asyncio.sleep(random.random() / 100)\n    return i * i\n\nresults, peak = asyncio.run(bounded_gather([fetch(i) for i in range(30)], limit=5))\nprint(results[:8], \"... peak in flight:\", peak)",
            "label": null,
            "output": "[0, 1, 4, 9, 16, 25, 36, 49] ... peak in flight: 5",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>gather</code> preserves input order regardless of completion order, and the semaphore caps how many bodies run at once. Note the coroutine objects are all created up front; that is cheap, since a coroutine does nothing until awaited. For very large or unbounded inputs, use a fixed set of workers pulling from a queue instead, so you never hold millions of pending coroutines."
          }
        ]
      },
      {
        "q": "When should you not use asyncio at all?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "When the work is CPU-bound (asyncio adds overhead and no parallelism &mdash; use processes), when the important libraries have no async versions (you would wrap everything in <code>to_thread</code>, which is just a thread pool with extra steps), or when concurrency is low and a few threads would be simpler. asyncio shines with many concurrent, mostly-waiting I/O operations: thousands of sockets, websockets, proxies, crawlers, chat servers. It also &ldquo;colours&rdquo; functions: async functions can call sync ones but not the reverse without a loop, so adopting it is a whole-codebase decision."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Python docs: Developing with asyncio",
        "url": "https://docs.python.org/3/library/asyncio-dev.html"
      },
      {
        "label": "Python docs: Task groups and create_task",
        "url": "https://docs.python.org/3/library/asyncio-task.html"
      },
      {
        "label": "Python docs: asyncio synchronisation primitives",
        "url": "https://docs.python.org/3/library/asyncio-sync.html"
      },
      {
        "label": "PEP 654: Exception groups and except*",
        "url": "https://peps.python.org/pep-0654/"
      }
    ]
  }
];
