from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="bytecode",
    title="CPython Bytecode",
    intro=[
        "Python is compiled. Not to machine code, but to <strong>bytecode</strong>: a compact instruction set for a stack-based virtual machine. Every function you write becomes a code object holding those instructions, and a big loop in C &mdash; the evaluation loop &mdash; executes them one at a time.",
        "Reading bytecode answers questions that are otherwise folklore: why locals are faster than globals, why <code>UnboundLocalError</code> exists, what <code>a, b = b, a</code> really does, and what the 3.11+ &ldquo;faster CPython&rdquo; work actually changed.",
    ],
    sections=[
        section(
            "From source to bytecode",
            "Running a module goes through a fixed pipeline:",
            table(
                ["Stage", "Produces", "You can inspect it with"],
                [
                    ["Tokenizer", "A stream of tokens", "<code>tokenize</code>"],
                    ["Parser", "An abstract syntax tree", "<code>ast.parse</code>, <code>ast.dump</code>"],
                    ["Symbol table", "Which names are local, global, free or cell", "<code>symtable</code>"],
                    ["Compiler", "A code object: bytecode + constants + names", "<code>compile</code>, <code>dis</code>"],
                    ["Evaluation loop", "The running program", "<code>sys.settrace</code>, profilers"],
                ],
            ),
            code('''
                import ast

                tree = ast.parse("total = price * 2")
                print(ast.dump(tree.body[0], indent=2))
            ''', label="the AST for one statement"),
            code('''
                co = compile("total = price * 2", "<demo>", "exec")
                print(type(co).__name__)
                print("names: ", co.co_names)
                print("consts:", co.co_consts)

                import dis
                dis.dis(co)
            ''', label="the same statement, compiled"),
            "The code object keeps the bytecode separate from the data it refers to. Instructions carry small integer arguments that index into <code>co_names</code> (global and attribute names), <code>co_consts</code> (literals) or the local variable array.",
        ),
        section(
            "Reading dis output",
            "The virtual machine is a <em>stack machine</em>: instructions push values onto an evaluation stack and pop them off. Each <code>dis</code> line is an instruction, its argument, and in brackets what that argument means.",
            code('''
                import dis

                def area(width, height):
                    scale = 2
                    return width * height * scale

                dis.dis(area)
            '''),
            "Read it top to bottom: push <code>width</code> and <code>height</code>, multiply them (pop two, push one), push <code>scale</code>, multiply again, return the top of the stack. The numbers on the left are source line numbers. <code>RESUME</code> is a hook the interpreter uses for tracing and for checking whether it should switch threads.",
            caveat("Bytecode is not a stable interface. Instruction names and their arguments change in every minor release &mdash; 3.14 added <code>LOAD_SMALL_INT</code> and the <code>_BORROW</code> variants you see above. Use <code>dis</code> to understand, never to build tools that must survive an upgrade."),
        ),
        section(
            "Code objects and functions",
            "A code object is immutable and has no idea which module it lives in. A <em>function</em> is a code object bundled with the things needed to run it: its globals, default values, and closure cells.",
            code('''
                def make_counter(start=0):
                    count = start
                    def step(by=1):
                        nonlocal count
                        count += by
                        return count
                    return step

                step = make_counter(10)
                co = step.__code__

                print("name:      ", co.co_name)
                print("args:      ", co.co_argcount, co.co_varnames[:co.co_argcount])
                print("free vars: ", co.co_freevars)
                print("defaults:  ", step.__defaults__)
                print("closure:   ", step.__closure__[0].cell_contents)
                print(step(), step(5))
                print("closure:   ", step.__closure__[0].cell_contents)
            '''),
            "Many functions can share one code object: every call to <code>make_counter</code> creates a new <em>function</em> for <code>step</code>, but they all point at the same <code>__code__</code>, each with its own closure cell.",
        ),
        section(
            "Locals are array slots, globals are dict lookups",
            "The compiler decides at compile time whether every name is local, global or a closure variable, and emits a different instruction for each.",
            code('''
                import dis

                LIMIT = 10

                def check(value):
                    return value < LIMIT and len(str(value)) > 1

                dis.dis(check)
            '''),
            table(
                ["Instruction", "Where it looks", "Cost"],
                [
                    ["<code>LOAD_FAST</code>", "Slot <em>n</em> of the frame&rsquo;s local array", "An index"],
                    ["<code>LOAD_DEREF</code>", "A closure cell", "An index plus one pointer hop"],
                    ["<code>LOAD_GLOBAL</code>", "Module dict, then builtins dict", "Up to two hash lookups (cached by specialization)"],
                    ["<code>LOAD_ATTR</code>", "Instance dict, class MRO, descriptors", "Potentially many lookups (also specialized)"],
                ],
            ),
            "That is why the old trick of aliasing a global or a method to a local before a hot loop (<code>append = out.append</code>) used to help a lot. Since 3.11 the specializing interpreter caches most global and attribute lookups, so the gain is much smaller. Measure before doing it.",
            "Deciding scope at compile time has a visible consequence: if a function assigns to a name <em>anywhere</em>, that name is local for the <em>whole</em> function.",
            code('''
                x = 10

                def show():
                    print(x)      # compiled as LOAD_FAST: x is local here ...
                    x = 5         # ... because of this line

                show()
            ''', raises=True),
        ),
        section(
            "What the compiler optimises",
            "CPython&rsquo;s compiler is deliberately simple, but it does fold constants and pick better literal types when the result cannot change behaviour.",
            code('''
                def timeouts():
                    seconds = 24 * 60 * 60
                    banner = "-" * 10
                    return seconds, banner

                def is_vowel(c):
                    return c in ["a", "e", "i", "o", "u"]

                def is_digit(c):
                    return c in {"0", "1", "2"}

                print(timeouts.__code__.co_consts)
                print(is_vowel.__code__.co_consts)
                print(is_digit.__code__.co_consts)
            '''),
            "<code>24 * 60 * 60</code> became <code>86400</code> at compile time. A list literal used only for <code>in</code> became a tuple (a list would have to be rebuilt on every call), and a set literal became a <code>frozenset</code> constant.",
            "Equal constants are also stored once per compilation &mdash; the whole module, including every function in it, shares them. That is the real reason behind a famous identity puzzle (see the interview questions below).",
        ),
        section(
            "Comprehensions, generators and flags",
            "The compiler marks special kinds of function with flags in <code>co_flags</code>. Calling a function whose code has the <code>GENERATOR</code> flag does not run the body at all &mdash; it creates a generator object that will run it on demand.",
            code('''
                import inspect

                def plain():  return 1
                def gen():    yield 1
                async def coro(): return 1

                for fn in (plain, gen, coro):
                    flags = inspect.CO_GENERATOR | inspect.CO_COROUTINE
                    kind = {inspect.CO_GENERATOR: "generator",
                            inspect.CO_COROUTINE: "coroutine"}.get(fn.__code__.co_flags & flags, "plain")
                    print(f"{fn.__name__:6} -> {kind}")
            '''),
            "Since 3.12, list, dict and set comprehensions are <em>inlined</em> (PEP 709): instead of building and calling a hidden function, the compiler emits the loop directly into the enclosing function, which makes them up to twice as fast. Generator expressions still get their own code object, because they must be able to pause.",
            code('''
                import dis

                def squares(n):
                    return [i * i for i in range(n)]

                ops = {ins.opname for ins in dis.get_instructions(squares)}
                print("calls a hidden function:", "CALL" in ops and "MAKE_FUNCTION" in ops)
                print("loops in place:         ", "FOR_ITER" in ops)
            '''),
        ),
        section(
            "The specializing adaptive interpreter",
            "Python 3.11 made the evaluation loop adaptive (PEP 659). Each generic instruction watches the types it actually sees. After a few executions with the same types it rewrites itself in place into a specialized version with a fast path and a cheap guard. If the guard ever fails, it falls back and may re-specialize.",
            code('''
                import dis

                def add_all(values):
                    total = 0
                    for v in values:
                        total = total + v
                    return total

                for _ in range(100):
                    add_all([1, 2, 3])

                for ins in dis.get_instructions(add_all, adaptive=True):
                    if ins.opname.startswith(("BINARY_OP", "FOR_ITER")):
                        print(ins.opname)
            ''', label="after warming up on ints and lists"),
            "<code>BINARY_OP</code> became an int-only add and <code>FOR_ITER</code> became a list-only iterator. Code that keeps its types stable &mdash; a variable is always an int, an attribute is always found in the same place &mdash; stays on these fast paths. Code that mixes types in one hot spot keeps falling back to the generic version.",
            "Later releases build on this: 3.13 added an experimental copy-and-patch JIT (off by default), and 3.14 can build the interpreter as a chain of tail calls for a further speed-up on supported compilers.",
        ),
        section(
            ".pyc files",
            "Compiling is not free, so when a module is imported CPython caches the code object in <code>__pycache__/name.cpython-314.pyc</code>. The file is a 16-byte header followed by the marshalled code object.",
            code('''
                import importlib.util, marshal, pathlib, py_compile, struct, tempfile

                with tempfile.TemporaryDirectory() as d:
                    src = pathlib.Path(d, "mod.py")
                    src.write_text("def hello():\\n    return 'hi'\\n")
                    pyc = pathlib.Path(py_compile.compile(str(src), cfile=str(src) + "c"))
                    data = pyc.read_bytes()

                print("magic matches this interpreter:", data[:4] == importlib.util.MAGIC_NUMBER)
                flags, = struct.unpack("<I", data[4:8])
                print("flags (0 = invalidate by timestamp):", flags)
                code_obj = marshal.loads(data[16:])
                print("module constants:", [type(c).__name__ for c in code_obj.co_consts])
            '''),
            "The magic number changes whenever the bytecode format changes, so a <code>.pyc</code> from another version is ignored. The rest of the header is either the source&rsquo;s modification time and size, or (PEP 552) a hash of the source &mdash; useful for reproducible builds.",
            note("A <code>.pyc</code> only saves compile time at import. It does not make the code run any faster once loaded, and the main script you run directly is never cached."),
        ),
    ],
    questions=[
        question(
            "Is Python compiled or interpreted?",
            "medium",
            "Both, and saying only one is the wrong answer. CPython compiles source to bytecode ahead of execution (and caches it as <code>.pyc</code>), then interprets that bytecode in a virtual machine. Syntax errors anywhere in a file are reported before the first line runs, which proves the compile step exists:",
            code('''
                source = """
                print("first line")
                def broken(:
                    pass
                """
                try:
                    exec(compile(source, "demo.py", "exec"))
                except SyntaxError as e:
                    print("SyntaxError on line", e.lineno, "- and nothing printed")
            '''),
            "PyPy goes further and JIT-compiles hot loops to machine code; CPython 3.13+ has an experimental JIT too. &ldquo;Interpreted&rdquo; describes an implementation, not the language.",
        ),
        question(
            "Why does this raise <code>UnboundLocalError</code> instead of printing 10?",
            "medium",
            code('''
                count = 10
                def report():
                    print(count)
                    count += 1
                report()
            ''', raises=True),
            "Scope is decided by the compiler, for the whole function, before it runs. Because <code>count</code> is assigned somewhere in <code>report</code>, it is a local variable everywhere in <code>report</code>, and the compiler emits <code>LOAD_FAST</code> for the <code>print</code> line too. At run time that slot is still empty. Fix it with <code>global count</code> (or <code>nonlocal</code> in a closure) &mdash; or better, pass the value in and return the new one.",
        ),
        question(
            "What does <code>a, b = b, a</code> compile to? Is a tuple created?",
            "hard",
            code('''
                import dis
                def swap(a, b):
                    a, b = b, a
                    return a, b
                dis.dis(swap)
            '''),
            "No tuple is built. The compiler pushes <code>b</code> then <code>a</code> onto the stack and pops them straight back into the targets &mdash; the top of the stack (old <code>a</code>) goes into <code>b</code>, the next (old <code>b</code>) into <code>a</code>. Older versions pushed in source order and inserted a <code>ROT_TWO</code> or <code>SWAP</code> instruction; 3.14 simply reorders the stores so no swap is needed.",
            "What makes it safe is the language rule underneath: the whole right-hand side is evaluated before any name is assigned. The optimisation only applies to two or three targets &mdash; with four or more, CPython really does <code>BUILD_TUPLE</code> and <code>UNPACK_SEQUENCE</code>.",
        ),
        question(
            "Why can the same integer literal give <code>is</code> = <code>True</code> in a script and <code>False</code> in the REPL?",
            "hard",
            "In a script the whole module is compiled in one go, and equal constants in one compilation are stored once, so both names get the same object. In the REPL each line you type is compiled separately, so each <code>1000</code> is its own constant and its own object.",
            code('''
                ns = {}
                exec(compile("a = 1000\\nb = 1000", "<one unit>", "exec"), ns)
                print("one compile:  ", ns["a"] is ns["b"])

                ns = {}
                exec(compile("a = 1000", "<line 1>", "exec"), ns)
                exec(compile("b = 1000", "<line 2>", "exec"), ns)
                print("two compiles: ", ns["a"] is ns["b"])
            '''),
            "Neither result is guaranteed by the language &mdash; which is the real answer. Use <code>==</code> for values.",
        ),
        question(
            "What is in a <code>.pyc</code> file, when is it regenerated, and does it make code faster?",
            "medium",
            "A 16-byte header (magic number, flags, then either source mtime+size or a source hash) followed by the marshalled module code object. On import, CPython compares the header with the current source; if the magic number or timestamp does not match, it recompiles and rewrites the file.",
            "It only speeds up <em>import</em>, by skipping parsing and compiling. Execution speed is identical. The script you run directly (<code>python app.py</code>) is compiled every time and never cached; only imported modules are.",
        ),
        question(
            "What is the specializing adaptive interpreter, and how should it change the way you write hot code?",
            "hard",
            "Since 3.11 (PEP 659), generic instructions like <code>LOAD_ATTR</code>, <code>BINARY_OP</code> and <code>CALL</code> record the types they see and rewrite themselves into specialized versions &mdash; for example <code>LOAD_ATTR_INSTANCE_VALUE</code>, which reads an attribute at a known offset after a single type-version check. It is why 3.11 was 10&ndash;60% faster than 3.10 on typical code.",
            "The practical rule is <em>type stability</em>: keep the types flowing through a hot spot consistent. A function that sometimes gets ints and sometimes floats, or instances whose attributes are added in different orders, keeps de-specializing. Micro-tricks like caching globals in locals matter much less than they did.",
            code('''
                import dis

                def add(a, b):
                    return a + b

                for _ in range(100):
                    add(1.5, 2.5)
                print([i.opname for i in dis.get_instructions(add, adaptive=True) if "BINARY" in i.opname])
            ''', label="specialized for floats"),
        ),
    ],
    refs=[
        ("Python docs: dis — Disassembler for Python bytecode", "https://docs.python.org/3/library/dis.html"),
        ("PEP 659 — Specializing adaptive interpreter", "https://peps.python.org/pep-0659/"),
        ("PEP 709 — Inlined comprehensions", "https://peps.python.org/pep-0709/"),
        ("CPython internals: the bytecode interpreter", "https://github.com/python/cpython/blob/main/InternalDocs/interpreter.md"),
    ],
)
