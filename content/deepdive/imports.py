from ._blocks import code, table, note, caveat, section, question

# Most examples write real module files into a temporary directory and put it
# on sys.path, so circular imports, packages and reloads run for real. They
# print module names, never paths, so the captured output is stable.

TOPIC = dict(
    id="import-system",
    title="The Import System",
    intro=[
        "<code>import x</code> looks like a declaration, but it is an ordinary statement that runs at run time: it finds a file, executes it top to bottom to build a module object, caches that object, and binds a name. Almost every confusing import bug &mdash; circular imports, a change that &ldquo;didn&rsquo;t take&rdquo;, a module imported twice, <code>from x import y</code> seeing a stale value &mdash; follows directly from those four steps.",
        "This topic walks through the steps, then through packages, relative imports, circular imports, <code>__main__</code>, reloading, lazy loading and finally the hooks that let you import from anywhere.",
    ],
    sections=[
        section(
            "What import actually does",
            "<code>import spam</code> does this:",
            "1. Look in <code>sys.modules</code>. If <code>\"spam\"</code> is there, use that object and stop.<br>2. Otherwise ask each <em>finder</em> on <code>sys.meta_path</code> for a <em>module spec</em> (where it is, how to load it).<br>3. Create an empty module object, <strong>put it in <code>sys.modules</code> first</strong>, then execute the module's code with that object's <code>__dict__</code> as globals.<br>4. Bind the name <code>spam</code> in the importing namespace.",
            code('''
                import sys, tempfile, pathlib

                tmp = pathlib.Path(tempfile.mkdtemp())
                (tmp / "spam.py").write_text(
                    'print("  executing spam.py")\\n'
                    'value = 42\\n'
                )
                sys.path.insert(0, str(tmp))

                print("in cache before:", "spam" in sys.modules)
                import spam
                print("in cache after: ", "spam" in sys.modules)
                import spam                        # cache hit: nothing printed
                import spam as again
                print(again is spam is sys.modules["spam"], spam.value)
                print(type(spam).__name__, spam.__name__, spam.__spec__.loader.__class__.__name__)
            '''),
            "Module code runs <strong>once per process</strong>, however many times and from however many files it is imported. That is why module-level code is the natural place for configuration and singletons, and also why expensive work at import time slows down every program that touches the module.",
            note("A module is just an object whose attributes are its global variables. <code>spam.value</code> is <code>spam.__dict__[\"value\"]</code>."),
        ),
        section(
            "import x vs from x import y",
            "<code>import x</code> binds the module. <code>from x import y</code> imports the module the same way, then copies the <em>current</em> value of <code>x.y</code> into a new local name. If <code>x</code> later rebinds <code>y</code>, your copy does not change.",
            code('''
                import sys, tempfile, pathlib
                tmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))

                (tmp / "settings.py").write_text(
                    "debug = False\\n"
                    "def enable():\\n"
                    "    global debug\\n"
                    "    debug = True\\n"
                )

                import settings
                from settings import debug           # a copy of the binding, taken now

                settings.enable()
                print("settings.debug:", settings.debug)   # reads the module's current value
                print("debug:         ", debug)            # still the old object
            '''),
            "This is also why monkeypatching in tests has to target the module that <em>uses</em> a name. If <code>app.py</code> did <code>from time import sleep</code>, patching <code>time.sleep</code> does nothing to <code>app.sleep</code>; patch <code>app.sleep</code> instead.",
            table(
                ["Form", "Binds", "Sees later rebinding?"],
                [
                    ["<code>import pkg.mod</code>", "<code>pkg</code> (the top-level package)", "Yes, via <code>pkg.mod.name</code>"],
                    ["<code>import pkg.mod as m</code>", "<code>m</code> = the submodule", "Yes, via <code>m.name</code>"],
                    ["<code>from pkg.mod import name</code>", "<code>name</code> = the object right now", "No"],
                    ["<code>from pkg import mod</code>", "<code>mod</code> = the submodule", "Yes, via <code>mod.name</code>"],
                ],
            ),
        ),
        section(
            "Where Python looks: sys.path and finders",
            "The default finders search <code>sys.path</code> in order: the script's directory (or the current directory for <code>-m</code> and the REPL), <code>PYTHONPATH</code>, the standard library, then <code>site-packages</code>. The first match wins, which is how a local file called <code>random.py</code> or <code>email.py</code> breaks the standard library module with the same name.",
            code('''
                import sys, importlib.util

                print([getattr(f, "__name__", type(f).__name__) for f in sys.meta_path])

                for name in ("json", "math", "sys", "os", "not_a_real_module"):
                    spec = importlib.util.find_spec(name)
                    if spec is None:
                        print(f"{name:18} not found")
                        continue
                    loader = getattr(spec.loader, "__name__", type(spec.loader).__name__)
                    kind = spec.origin if spec.origin in ("built-in", "frozen") else spec.origin.rsplit(".", 1)[-1]
                    print(f"{name:18} loader={loader:22} origin={kind}")
            '''),
            "Built-in modules like <code>sys</code> are compiled into the interpreter; <code>math</code> is usually a C extension (<code>.so</code>/<code>.pyd</code>); <code>json</code> is a package of <code>.py</code> files. All three come back as the same kind of module object.",
            caveat("CPython also <em>freezes</em> a few startup modules (like <code>os</code> and <code>codecs</code>) into the binary for faster start-up, so their spec says <code>frozen</code> rather than pointing at a file."),
        ),
        section(
            "Packages and relative imports",
            "A <strong>package</strong> is a module with a <code>__path__</code>: a directory that can contain submodules. Importing <code>pkg.sub</code> imports <code>pkg</code> first (running its <code>__init__.py</code>), then <code>pkg.sub</code>, and sets <code>sub</code> as an attribute on <code>pkg</code>. A directory without <code>__init__.py</code> still imports, as a <em>namespace package</em> that can be spread across several directories.",
            code('''
                import sys, tempfile, pathlib
                tmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))

                pkg = tmp / "shop"; (pkg / "models").mkdir(parents=True)
                (pkg / "__init__.py").write_text('print("  init shop")\\nVERSION = "1.0"\\n')
                (pkg / "models" / "__init__.py").write_text('print("  init shop.models")\\n')
                (pkg / "models" / "order.py").write_text(
                    "from .. import VERSION          # up one package\\n"
                    "from . import line              # sibling module\\n"
                    "def describe():\\n"
                    "    return f'order v{VERSION} with {line.KIND}'\\n"
                )
                (pkg / "models" / "line.py").write_text('KIND = "line items"\\n')

                import shop.models.order
                print(shop.models.order.describe())
                print(shop.models.order.__package__, "|", "shop.models.line" in sys.modules)
                print(hasattr(shop, "__path__"), hasattr(shop.models.order, "__path__"))
            '''),
            "Relative imports resolve against the module's <code>__package__</code>, not against the file system. A file run directly as a script has <code>__name__ == \"__main__\"</code> and no package, so its relative imports fail. Run it as a module instead: <code>python -m shop.models.order</code>.",
            code('''
                import subprocess, sys, tempfile, pathlib
                tmp = pathlib.Path(tempfile.mkdtemp())
                (tmp / "app").mkdir()
                (tmp / "app" / "__init__.py").write_text("")
                (tmp / "app" / "util.py").write_text("NAME = 'util'\\n")
                (tmp / "app" / "main.py").write_text(
                    "from .util import NAME\\nprint('ok, imported', NAME, 'as', __name__)\\n")

                def run(*args):
                    p = subprocess.run([sys.executable, *args], cwd=tmp, capture_output=True, text=True)
                    return (p.stdout or p.stderr.strip().splitlines()[-1]).strip()

                print("python app/main.py ->", run("app/main.py"))
                print("python -m app.main ->", run("-m", "app.main"))
            '''),
        ),
        section(
            "Circular imports",
            "Step 3 above is the key to circular imports: a module is placed in <code>sys.modules</code> <em>before</em> its code runs. If <code>a</code> imports <code>b</code> and <code>b</code> imports <code>a</code>, the second import does not loop forever &mdash; it gets the half-built <code>a</code> from the cache. Anything <code>a</code> has not defined yet is missing.",
            code('''
                import sys, tempfile, pathlib
                tmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))

                (tmp / "orders.py").write_text(
                    "import customers\\n"
                    "def total(): return 100\\n"
                )
                (tmp / "customers.py").write_text(
                    "from orders import total     # orders is only half executed\\n"
                    "def spend(): return total()\\n"
                )
                try:
                    import orders
                except ImportError as e:
                    print("ImportError:", str(e).rsplit(" (/", 1)[0])    # drop the temp path
            '''),
            "Recent Python versions even name the cause in the message (&ldquo;most likely due to a circular import&rdquo;). There are three standard fixes, in order of preference:",
            "1. <strong>Restructure</strong>: move what both modules need into a third module that imports neither.<br>2. <strong>Import the module, not the name</strong>: <code>import orders</code> and call <code>orders.total()</code> inside the function, so the lookup happens at call time, after both modules have finished.<br>3. <strong>Import inside the function</strong> that needs it, deferring the import until it runs.",
            code('''
                import sys, tempfile, pathlib
                tmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))

                (tmp / "orders.py").write_text(
                    "import customers\\n"
                    "def total(): return 100\\n"
                )
                (tmp / "customers.py").write_text(
                    "import orders                  # just the (half-built) module object\\n"
                    "def spend(): return orders.total() * 2   # looked up at call time\\n"
                )
                import orders, customers
                print(customers.spend())
            '''),
            caveat("<code>from typing import TYPE_CHECKING</code> plus <code>if TYPE_CHECKING: from orders import Order</code> is the usual way to break a cycle that exists only for type hints: the import runs for the type checker, never at run time."),
        ),
        section(
            "__name__, __main__ and the double-import trap",
            "The file you run is executed as the module <code>__main__</code>, not under its file name. If another module then imports it by name, Python finds no <code>\"script\"</code> in <code>sys.modules</code> and executes the file a <em>second</em> time as a separate module. Two copies means two sets of globals and two different classes with the same name.",
            code('''
                import subprocess, sys, tempfile, pathlib
                tmp = pathlib.Path(tempfile.mkdtemp())
                (tmp / "registry.py").write_text(
                    "print(f'  running registry.py as {__name__!r}')\\n"
                    "items = []\\n"
                    "if __name__ == '__main__':\\n"
                    "    items.append('from main')\\n"
                    "    import helper\\n"
                    "    print('  __main__.items =', items)\\n"
                )
                (tmp / "helper.py").write_text(
                    "import registry\\n"
                    "print('  registry.items  =', registry.items)\\n"
                )
                print(subprocess.run([sys.executable, "registry.py"], cwd=tmp,
                                     capture_output=True, text=True).stdout.rstrip())
            '''),
            note("Keep scripts thin: put logic in importable modules and make the entry point a small <code>main()</code> called under <code>if __name__ == \"__main__\":</code>, or run it with <code>python -m package.module</code>."),
        ),
        section(
            "Reloading, lazy loading and module __getattr__",
            "<code>importlib.reload(mod)</code> re-executes the module's code <em>into the same module object</em>. Code that holds the module sees new values; code that copied names with <code>from mod import x</code>, and instances of the old classes, do not.",
            code('''
                import sys, tempfile, pathlib, importlib
                tmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))
                src = tmp / "shapes.py"

                src.write_text("class Square:\\n    sides = 4\\nRATE = 1\\n")
                import shapes
                from shapes import RATE
                old_obj = shapes.Square()

                src.write_text("class Square:\\n    sides = 4\\nRATE = 2\\n")
                importlib.invalidate_caches()
                same = importlib.reload(shapes)

                print(same is shapes, shapes.RATE, RATE)
                print(isinstance(old_obj, shapes.Square))   # old instance, new class object
            '''),
            "Python 3.7 added module-level <code>__getattr__</code> and <code>__dir__</code> (PEP 562). They let a module compute attributes on demand &mdash; for deprecation warnings, or to defer importing a heavy submodule until someone actually uses it.",
            code('''
                import sys, tempfile, pathlib
                tmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))
                (tmp / "toolkit").mkdir()
                (tmp / "toolkit" / "__init__.py").write_text(
                    "import importlib\\n"
                    "_LAZY = {'plotting'}\\n"
                    "def __getattr__(name):\\n"
                    "    if name in _LAZY:\\n"
                    "        mod = importlib.import_module(f'.{name}', __name__)\\n"
                    "        globals()[name] = mod          # cache: next access is a plain lookup\\n"
                    "        return mod\\n"
                    "    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')\\n"
                )
                (tmp / "toolkit" / "plotting.py").write_text("print('  (expensive plotting import)')\\ndef plot(): return 'plotted'\\n")

                import toolkit
                print("plotting loaded?", "toolkit.plotting" in sys.modules)
                print(toolkit.plotting.plot())
                print("plotting loaded?", "toolkit.plotting" in sys.modules)
            '''),
        ),
        section(
            "Import hooks: importing from anywhere",
            "Finders on <code>sys.meta_path</code> are ordinary objects with a <code>find_spec</code> method. Add your own and <code>import</code> can load modules from a database, a zip in memory, a URL or generated source. This is how pytest rewrites <code>assert</code> statements, and how tools like editable installs work.",
            code('''
                import sys, importlib.abc, importlib.util

                SOURCES = {
                    "virtual_math": "def double(x):\\n    return 2 * x\\n",
                    "virtual_greet": "NAME = 'from a dict'\\n",
                }

                class DictFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
                    def find_spec(self, name, path, target=None):
                        if name in SOURCES:
                            return importlib.util.spec_from_loader(name, self, origin="dict")
                        return None                      # let the next finder try

                    def create_module(self, spec):
                        return None                      # default module object

                    def exec_module(self, module):
                        exec(SOURCES[module.__name__], module.__dict__)

                sys.meta_path.insert(0, DictFinder())

                import virtual_math, virtual_greet
                print(virtual_math.double(21), virtual_greet.NAME, virtual_math.__spec__.origin)
            '''),
        ),
    ],
    questions=[
        question(
            "Why does a module's top-level code run only once, even if twenty files import it?",
            "medium",
            "The first import puts the module object in <code>sys.modules</code>; every later <code>import</code> statement checks that dict first and just binds the cached object. Deleting the entry (<code>del sys.modules[\"m\"]</code>) makes the next import execute the file again and produce a <em>new</em> module object &mdash; while everything that imported the old one keeps it.",
            code('''
                import sys, tempfile, pathlib
                tmp = pathlib.Path(tempfile.mkdtemp()); sys.path.insert(0, str(tmp))
                (tmp / "counter.py").write_text("print('  executing counter.py')\\nhits = 0\\n")

                import counter
                counter.hits += 1
                import counter                   # cached, still hits == 1
                first = counter
                del sys.modules["counter"]
                import counter                   # executes again: a brand new module
                print(first.hits, counter.hits, first is counter)
            '''),
        ),
        question(
            "Explain how a circular import fails with <code>ImportError: cannot import name</code> but works with <code>import module</code>.",
            "hard",
            "When <code>a</code> starts executing, it is already in <code>sys.modules</code> as an empty-ish module. If it imports <code>b</code>, and <code>b</code> does <code>from a import f</code>, the import system finds the partly built <code>a</code> in the cache and tries to read <code>a.f</code> immediately &mdash; but <code>a</code> has not reached <code>def f</code> yet, so the name lookup fails.",
            "<code>import a</code> in <code>b</code> only binds the module object, which already exists. The attribute lookup <code>a.f</code> is postponed to when <code>b</code>'s function actually runs, by which time <code>a</code> has finished executing. Same cycle, but no name is needed before it exists. The better fix is still to remove the cycle by moving shared code into a third module.",
        ),
        question(
            "You changed a library file but the running program still behaves the old way. List the reasons.",
            "medium",
            "<strong>sys.modules cache</strong>: the module was imported before the edit and is never re-read. Restart, or <code>importlib.reload</code> with its caveats. <strong>Stale names</strong>: even after a reload, <code>from lib import f</code> elsewhere still holds the old <code>f</code>, and existing instances keep their old class. <strong>A different copy</strong>: <code>sys.path</code> found another <code>lib</code> earlier (an installed version shadowing your editable checkout); check <code>lib.__file__</code>. <strong>Stale bytecode</strong> is rarely the cause: CPython compares the source's modification time against the <code>.pyc</code> header and recompiles.",
            code('''
                import json, importlib.util
                print(json.__name__, "from", json.__spec__.origin.rsplit("/", 2)[-2] + "/" + json.__spec__.origin.rsplit("/", 1)[-1])
                print("cached at:", importlib.util.cache_from_source("lib.py"))
            '''),
        ),
        question(
            "What is the difference between running <code>python pkg/tool.py</code> and <code>python -m pkg.tool</code>?",
            "medium",
            "<code>python pkg/tool.py</code> runs the file as <code>__main__</code> with no package, and puts <code>pkg/</code> (the script's directory) at the front of <code>sys.path</code>. Relative imports fail, and absolute imports of <code>pkg.something</code> only work if the project root happens to be importable.",
            "<code>python -m pkg.tool</code> imports <code>pkg</code> first (running its <code>__init__</code>), runs <code>tool</code> as <code>__main__</code> with <code>__package__ = \"pkg\"</code>, and puts the current directory on <code>sys.path</code>. Relative imports work and the module is found the same way any other code would find it. For anything inside a package, <code>-m</code> is the right way to run it.",
        ),
        question(
            "How would you make <code>import heavy_lib</code> at the top of a CLI not slow down <code>--help</code>?",
            "hard",
            "Options, from simplest: move the import inside the function that needs it (imports after the first are a dict lookup, so the repeated cost is negligible); use a module-level <code>__getattr__</code> in your own package to import submodules on first attribute access; or use <code>importlib.util.LazyLoader</code>, which returns a module object whose code runs on first attribute access.",
            code('''
                import sys, importlib.util

                def lazy_import(name):
                    spec = importlib.util.find_spec(name)
                    loader = importlib.util.LazyLoader(spec.loader)
                    spec.loader = loader
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[name] = module
                    loader.exec_module(module)          # does NOT run the module yet
                    return module

                decimal = lazy_import("decimal")
                print(type(decimal).__name__)           # a lazy module proxy
                print(decimal.Decimal("1.10") + decimal.Decimal("2.205"))   # first use runs it
                print(type(decimal).__name__)
            '''),
            "Measure first with <code>python -X importtime -c \"import yourcli\"</code>, which prints the time spent in every import, nested.",
        ),
    ],
    refs=[
        ("Python docs: The import system", "https://docs.python.org/3/reference/import.html"),
        ("Python docs: importlib", "https://docs.python.org/3/library/importlib.html"),
        ("Python docs: __main__", "https://docs.python.org/3/library/__main__.html"),
        ("PEP 562: Module __getattr__ and __dir__", "https://peps.python.org/pep-0562/"),
        ("PEP 420: Implicit namespace packages", "https://peps.python.org/pep-0420/"),
    ],
)
