from ._lld import code, table, note, caveat, question, problem

DOC_EXPORT = problem(
    id="document-export",
    title="Design a Document Model with Multiple Export Formats",
    level="medium",
    patterns=["Visitor", "Composite", "Builder"],
    summary="A document tree of elements exported to HTML, Markdown and plain text, plus word count - without touching element classes.",
    statement=[
        "Design the document model of a report generator. Documents contain sections, headings, paragraphs, lists and tables (sections nest). The same document must be exported to HTML, Markdown and plain text, and new outputs (PDF, a word count, a table of contents) keep being requested.",
    ],
    requirements=[
        "Stable set of element types; growing set of operations over them. Operations must traverse nested sections. Building a document should read well in code.",
    ],
    choose=[
        ["Many new operations over a fixed set of element types", "Visitor", "Each export is one visitor class; element classes never change"],
        ["Sections contain elements, including other sections", "Composite", "A section's <code>accept</code> visits its children"],
        ["Assembling a document in code", "Builder", "Fluent <code>.heading().para().bullets()</code> with nested sections"],
    ],
    classes=[
        ["<code>Element</code> subclasses", "Heading, Paragraph, BulletList, Section; each has <code>accept(visitor)</code>"],
        ["<code>HtmlExporter</code>, <code>MarkdownExporter</code>, <code>WordCounter</code>", "Visitors with one method per element type"],
        ["<code>DocBuilder</code>", "Fluent construction with nested sections"],
    ],
    implementation=[
        code('''
            from dataclasses import dataclass, field

            class Element:
                def accept(self, v):
                    return getattr(v, "visit_" + type(self).__name__.lower())(self)   # double dispatch

            @dataclass
            class Heading(Element):
                text: str
                level: int = 1

            @dataclass
            class Paragraph(Element):
                text: str

            @dataclass
            class BulletList(Element):
                items: list

            @dataclass
            class Section(Element):
                title: str
                children: list = field(default_factory=list)

            class HtmlExporter:
                def visit_heading(self, h): return f"<h{h.level}>{h.text}</h{h.level}>"
                def visit_paragraph(self, p): return f"<p>{p.text}</p>"
                def visit_bulletlist(self, b): return "<ul>" + "".join(f"<li>{i}</li>" for i in b.items) + "</ul>"
                def visit_section(self, s):
                    return f'<section><h2>{s.title}</h2>{"".join(c.accept(self) for c in s.children)}</section>'

            class MarkdownExporter:
                def __init__(self): self.depth = 1
                def visit_heading(self, h): return "#" * h.level + " " + h.text
                def visit_paragraph(self, p): return p.text
                def visit_bulletlist(self, b): return "\\n".join(f"- {i}" for i in b.items)
                def visit_section(self, s):
                    self.depth += 1
                    body = [("#" * self.depth) + " " + s.title] + [c.accept(self) for c in s.children]
                    self.depth -= 1
                    return "\\n\\n".join(body)

            class WordCounter:
                def visit_heading(self, h): return len(h.text.split())
                def visit_paragraph(self, p): return len(p.text.split())
                def visit_bulletlist(self, b): return sum(len(i.split()) for i in b.items)
                def visit_section(self, s): return len(s.title.split()) + sum(c.accept(self) for c in s.children)

            class DocBuilder:
                def __init__(self): self.stack = [Section("root")]
                def _add(self, e): self.stack[-1].children.append(e); return self
                def heading(self, t, level=1): return self._add(Heading(t, level))
                def para(self, t): return self._add(Paragraph(t))
                def bullets(self, *items): return self._add(BulletList(list(items)))
                def section(self, title):
                    s = Section(title); self._add(s); self.stack.append(s); return self
                def end(self): self.stack.pop(); return self
                def build(self): return self.stack[0].children

            doc = (DocBuilder()
                   .heading("Q3 Report")
                   .para("Revenue grew in every region.")
                   .section("Highlights").bullets("North +12%", "South +7%")
                       .section("Risks").para("Supply costs are rising.").end()
                   .end()
                   .build())

            print("".join(e.accept(HtmlExporter()) for e in doc))
            md = MarkdownExporter()
            print("\\n\\n".join(e.accept(md) for e in doc))
            print("words:", sum(e.accept(WordCounter()) for e in doc))
        '''),
        "Adding the word counter required no change to any element class. Adding a new element type (an image) would require a method in every visitor; that is the trade-off Visitor makes, and it is the right one here because outputs grow faster than element types.",
    ],
    extend=[
        "A table-of-contents visitor collects headings and section titles with their depth. PDF export is another visitor driving a PDF library. If element types ever need to grow fast, switch the dispatch to <code>functools.singledispatch</code> functions so a missing case fails loudly at one registration point.",
    ],
    questions=[
        question(
            "What is double dispatch, and how does <code>accept</code> achieve it here?",
            "hard",
            "The method that runs depends on two types: the element's and the visitor's. A normal method call dispatches on one (the receiver). <code>element.accept(visitor)</code> dispatches on the element's type, and inside it the element calls the visitor method named for its own type (<code>visit_paragraph</code>), dispatching on the visitor's type. Python can shortcut this with <code>getattr</code> by name or with <code>singledispatch</code> on the element type.",
        ),
        question(
            "When would you not use Visitor for exports?",
            "medium",
            "When element types change often (every new type touches every visitor), when there are only one or two operations (a method per class is simpler), or when operations need private state of the elements (visitors only see the public interface). For a handful of formats over a stable model, Visitor keeps each format in one file, which is the main win.",
        ),
    ],
)


EXPRESSION_EVALUATOR = problem(
    id="expression-evaluator",
    title="Design an Expression Evaluator (Calculator)",
    level="medium",
    patterns=["Interpreter", "Composite", "Visitor"],
    summary="Tokenise, parse into an AST with precedence, evaluate with variables, and pretty-print - each a separate component.",
    statement=[
        "Design a calculator that evaluates expressions like <code>2 * (x + 3) - y / 4</code> with variables, operator precedence and parentheses, and can also print the expression back in a normalised form. New operators (power, functions) will be added.",
    ],
    requirements=[
        "Operators + &minus; * / with standard precedence and left associativity, unary minus, parentheses, numbers and variables. Clear errors for syntax problems and unknown variables. Evaluation and printing are separate operations over the same parsed tree.",
    ],
    choose=[
        ["Grammar of a small language, evaluated over a tree", "Interpreter", "Each node type knows how to evaluate itself"],
        ["Expressions contain sub-expressions", "Composite", "<code>BinOp</code> holds two child expressions"],
        ["Printing, simplifying, compiling are more operations on the same tree", "Visitor", "Kept separate from the node classes (here: printing)"],
    ],
    classes=[
        ["<code>tokenize</code>", "String &rarr; tokens"],
        ["<code>Parser</code>", "Recursive descent: <code>expr</code> &rarr; <code>term</code> &rarr; <code>factor</code>"],
        ["<code>Num</code>, <code>Var</code>, <code>Neg</code>, <code>BinOp</code>", "AST nodes with <code>eval(env)</code>"],
        ["<code>to_str</code>", "Printer that adds only necessary parentheses"],
    ],
    implementation=[
        code('''
            import re
            from dataclasses import dataclass

            TOKEN = re.compile(r"\\s*(?:(\\d+\\.?\\d*)|([A-Za-z_]\\w*)|(.))")

            def tokenize(src):
                out = []
                for num, name, op in TOKEN.findall(src):
                    if num: out.append(("num", float(num)))
                    elif name: out.append(("var", name))
                    elif op.strip(): out.append(("op", op))
                return out + [("end", None)]

            @dataclass
            class Num:
                v: float
                def eval(self, env): return self.v

            @dataclass
            class Var:
                name: str
                def eval(self, env):
                    if self.name not in env:
                        raise NameError(f"unknown variable {self.name!r}")
                    return env[self.name]

            @dataclass
            class Neg:
                e: object
                def eval(self, env): return -self.e.eval(env)

            OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b}
            PREC = {"+": 1, "-": 1, "*": 2, "/": 2}

            @dataclass
            class BinOp:
                op: str
                l: object
                r: object
                def eval(self, env): return OPS[self.op](self.l.eval(env), self.r.eval(env))

            class Parser:
                """expr := term (('+'|'-') term)* ; term := factor (('*'|'/') factor)* ;
                   factor := num | var | '-' factor | '(' expr ')'"""
                def __init__(self, src): self.toks, self.i = tokenize(src), 0
                def peek(self): return self.toks[self.i]
                def take(self): self.i += 1; return self.toks[self.i - 1]

                def parse(self):
                    e = self.expr()
                    if self.peek()[0] != "end":
                        raise SyntaxError(f"unexpected {self.peek()[1]!r}")
                    return e

                def expr(self):
                    e = self.term()
                    while self.peek() in (("op", "+"), ("op", "-")):
                        e = BinOp(self.take()[1], e, self.term())       # left-associative
                    return e

                def term(self):
                    e = self.factor()
                    while self.peek() in (("op", "*"), ("op", "/")):
                        e = BinOp(self.take()[1], e, self.factor())
                    return e

                def factor(self):
                    kind, v = self.take()
                    if kind == "num": return Num(v)
                    if kind == "var": return Var(v)
                    if (kind, v) == ("op", "-"): return Neg(self.factor())
                    if (kind, v) == ("op", "("):
                        e = self.expr()
                        if self.take() != ("op", ")"):
                            raise SyntaxError("missing )")
                        return e
                    raise SyntaxError(f"unexpected {v!r}")

            def to_str(e, parent=0, right=False):                        # printing as a separate operation
                match e:
                    case Num(v): return f"{v:g}"
                    case Var(n): return n
                    case Neg(x): return "-" + to_str(x, 3)
                    case BinOp(op, l, r):
                        p = PREC[op]
                        s = f"{to_str(l, p)} {op} {to_str(r, p, right=True)}"
                        need = p < parent or (right and p == parent and op in "-/")
                        return f"({s})" if need else s

            env = {"x": 4, "y": 10}
            for src in ["2 * (x + 3) - y / 4", "((1 + 2)) + (3 * 4)", "10 - (4 - 3)", "10 - 4 - 3", "-(x - 1) * -2"]:
                tree = Parser(src).parse()
                print(f"{src:22} => {to_str(tree):18} = {tree.eval(env):g}")
            for bad in ["2 * (3 + 4", "2 + * 3", "z + 1"]:
                try:
                    print(Parser(bad).parse().eval(env))
                except (SyntaxError, NameError) as e:
                    print(f"{bad:22} => {type(e).__name__}: {e}")
        '''),
        "The printer removed redundant parentheses but kept the ones that matter: <code>10 - (4 - 3)</code> needs them because subtraction is not associative, while <code>((1 + 2)) + (3 * 4)</code> needs none.",
    ],
    extend=[
        "Exponentiation (right-associative, binds tighter than unary minus) is a new grammar level and an entry in <code>OPS</code>. Functions (<code>max(a, b)</code>) add a <code>Call</code> node. A simplifier (<code>x * 1 &rarr; x</code>, constant folding) is another tree-to-tree operation like the printer.",
    ],
    questions=[
        question(
            "How does the grammar encode precedence and associativity?",
            "medium",
            "Each precedence level is its own rule, and lower-precedence rules are built from higher ones: <code>expr</code> combines <code>term</code>s with + and &minus;, <code>term</code> combines <code>factor</code>s with * and /. So <code>2 + 3 * 4</code> parses the multiplication inside a <code>term</code> first. Left associativity comes from the loop that folds operands left to right (<code>((10 - 4) - 3)</code>); a right-associative operator would recurse on the right instead.",
        ),
        question(
            "Why not just call Python's <code>eval</code>?",
            "medium",
            "It executes arbitrary Python: <code>__import__('os').system(...)</code> in a user-supplied expression is remote code execution. Even with restricted globals it is hard to make safe. It also cannot give you a tree to print, analyse or transform. If you need Python syntax, parse with <code>ast.parse(src, mode=\"eval\")</code> and walk only an allow-listed set of node types.",
        ),
    ],
)


HTTP_MIDDLEWARE = problem(
    id="http-middleware",
    title="Design an HTTP Middleware Pipeline",
    level="medium",
    patterns=["Chain of Responsibility", "Decorator"],
    summary="Composable middleware (logging, auth, rate limit, error handling) wrapping a handler, with short-circuiting.",
    statement=[
        "Design the request pipeline of a small web framework. Each request passes through middleware &mdash; request id, logging, authentication, rate limiting, error handling &mdash; before reaching a route handler, and the response passes back through them in reverse. Any middleware may answer early (401, 429).",
    ],
    requirements=[
        "Middleware are composable and ordered. Each can modify the request, call the next layer, modify the response, or short-circuit. Exceptions from handlers become 500 responses. Adding a middleware must not change existing ones.",
    ],
    choose=[
        ["Request passes through handlers in order; any may stop it", "Chain of Responsibility", "Each middleware decides whether to call <code>next</code>"],
        ["Each layer wraps the rest and acts before and after", "Decorator", "Middleware has the same interface as a handler: request in, response out"],
    ],
    classes=[
        ["<code>Request</code>, <code>Response</code>", "Plain data"],
        ["Middleware", "Functions <code>(request, next) &rarr; response</code>"],
        ["<code>build_pipeline</code>", "Folds middleware around the final handler"],
    ],
    implementation=[
        code('''
            from dataclasses import dataclass, field
            from itertools import count
            from collections import defaultdict

            @dataclass
            class Request:
                path: str
                headers: dict = field(default_factory=dict)
                user: str | None = None
                ctx: dict = field(default_factory=dict)

            @dataclass
            class Response:
                status: int
                body: str
                headers: dict = field(default_factory=dict)

            _ids = count(1)
            def request_id(req, nxt):
                req.ctx["id"] = f"req-{next(_ids)}"
                resp = nxt(req)
                resp.headers["X-Request-Id"] = req.ctx["id"]
                return resp

            log = []
            def logging_mw(req, nxt):
                resp = nxt(req)
                log.append(f"{req.ctx['id']} {req.path} -> {resp.status}")
                return resp

            def errors(req, nxt):
                try:
                    return nxt(req)
                except Exception as e:
                    return Response(500, f"internal error ({type(e).__name__})")

            TOKENS = {"t-ann": "ann"}
            def auth(req, nxt):
                if req.path.startswith("/public"):
                    return nxt(req)
                user = TOKENS.get(req.headers.get("Authorization", ""))
                if not user:
                    return Response(401, "unauthorised")          # short-circuit
                req.user = user
                return nxt(req)

            def rate_limit(limit):
                seen = defaultdict(int)
                def mw(req, nxt):
                    key = req.user or "anon"
                    seen[key] += 1
                    if seen[key] > limit:
                        return Response(429, "slow down", {"Retry-After": "60"})
                    return nxt(req)
                return mw

            def router(req):
                if req.path == "/me": return Response(200, f"hello {req.user}")
                if req.path == "/public/ping": return Response(200, "pong")
                if req.path == "/boom": raise KeyError("bug")
                return Response(404, "not found")

            def build_pipeline(middleware, handler):
                for mw in reversed(middleware):                    # outermost first in the list
                    handler = (lambda m, n: lambda req: m(req, n))(mw, handler)
                return handler

            app = build_pipeline([request_id, logging_mw, errors, auth, rate_limit(2)], router)
            calls = [("/public/ping", {}), ("/me", {}), ("/me", {"Authorization": "t-ann"}),
                     ("/boom", {"Authorization": "t-ann"}), ("/me", {"Authorization": "t-ann"})]
            for path, headers in calls:
                r = app(Request(path, headers))
                print(r.status, r.body, r.headers)
            print(log)
        '''),
        "Order is the design. <code>errors</code> sits inside <code>logging_mw</code>, so the crashing request was logged as a 500 rather than escaping; <code>auth</code> runs before <code>rate_limit</code>, so limits are per user. The third authenticated call to <code>/me</code> was rate limited because <code>/boom</code> also counted.",
    ],
    extend=[
        "CORS, compression and caching are more middleware. Per-route middleware is a second pipeline built for each route. This is exactly how WSGI/ASGI middleware, Express and Django middleware work: each layer is a callable wrapping the next.",
    ],
    questions=[
        question(
            "Where should the error-handling middleware go in the chain, and why?",
            "medium",
            "Near the outside, so it catches exceptions from everything inside it (auth bugs, handler bugs) and converts them to a response &mdash; but inside the logging and request-id middleware, so failed requests are still logged with their id and the id header is still set. If it were innermost, an exception thrown by auth or rate limiting would escape unhandled.",
        ),
        question(
            "How is this both Chain of Responsibility and Decorator?",
            "medium",
            "Chain of Responsibility: a request is passed along a sequence of handlers, any of which can handle it and stop the chain (401, 429). Decorator: each middleware has the same interface as the handler it wraps and can add behaviour before and after the inner call (timing, headers). Middleware pipelines are the standard example of the two patterns being the same structure.",
        ),
    ],
)


QUERY_BUILDER = problem(
    id="query-builder",
    title="Design a SQL Query Builder",
    level="medium",
    patterns=["Builder", "Composite", "Interpreter"],
    summary="Fluent, immutable query construction with composable conditions and parameter binding (no string concatenation).",
    statement=[
        "Design a small query builder like SQLAlchemy Core or Knex: code builds <code>SELECT</code> queries fluently, conditions combine with AND/OR/NOT, and the output is SQL text plus bound parameters, never values pasted into the string.",
    ],
    requirements=[
        "<code>select(cols).from_(table).where(cond).order_by(col).limit(n)</code>. Conditions: comparisons, IN, AND/OR/NOT nested arbitrarily. Builders are immutable (each call returns a new builder), so a base query can be reused safely. Output <code>(sql, params)</code> with <code>?</code> placeholders.",
    ],
    choose=[
        ["Step-by-step construction of a complex object", "Builder", "Each clause is a method; <code>build()</code> renders"],
        ["Conditions nest: (a AND (b OR NOT c))", "Composite", "<code>And</code>/<code>Or</code>/<code>Not</code> contain conditions"],
        ["Conditions render themselves to SQL fragments", "Interpreter", "Each node knows its SQL and its parameters"],
    ],
    classes=[
        ["<code>Col</code>", "Column with operator methods producing conditions"],
        ["<code>Cond</code>, <code>And</code>, <code>Or</code>, <code>Not</code>", "Condition tree; <code>render()</code> &rarr; (sql, params)"],
        ["<code>Query</code>", "Immutable builder: each method returns a modified copy"],
    ],
    implementation=[
        code('''
            import sqlite3
            from dataclasses import dataclass, replace

            class Cond:
                def __and__(self, o): return And(self, o)
                def __or__(self, o): return Or(self, o)
                def __invert__(self): return Not(self)

            @dataclass(frozen=True)
            class Compare(Cond):
                col: str
                op: str
                value: object
                def render(self):
                    if self.op == "IN":
                        marks = ", ".join("?" * len(self.value))
                        return f"{self.col} IN ({marks})", list(self.value)
                    return f"{self.col} {self.op} ?", [self.value]

            @dataclass(frozen=True)
            class And(Cond):
                a: Cond
                b: Cond
                def render(self):
                    (sa, pa), (sb, pb) = self.a.render(), self.b.render()
                    return f"({sa} AND {sb})", pa + pb

            @dataclass(frozen=True)
            class Or(Cond):
                a: Cond
                b: Cond
                def render(self):
                    (sa, pa), (sb, pb) = self.a.render(), self.b.render()
                    return f"({sa} OR {sb})", pa + pb

            @dataclass(frozen=True)
            class Not(Cond):
                a: Cond
                def render(self):
                    s, p = self.a.render()
                    return f"NOT {s}", p

            class Col:
                def __init__(self, name):
                    if not name.isidentifier():
                        raise ValueError(f"bad column name {name!r}")
                    self.name = name
                def __eq__(self, v): return Compare(self.name, "=", v)
                def __gt__(self, v): return Compare(self.name, ">", v)
                def __lt__(self, v): return Compare(self.name, "<", v)
                def in_(self, values): return Compare(self.name, "IN", tuple(values))

            @dataclass(frozen=True)
            class Query:
                table: str = ""
                cols: tuple = ("*",)
                cond: Cond | None = None
                order: tuple = ()
                lim: int | None = None

                def select(self, *cols): return replace(self, cols=cols)
                def from_(self, t): return replace(self, table=t)
                def where(self, c): return replace(self, cond=c if self.cond is None else self.cond & c)
                def order_by(self, *cols): return replace(self, order=cols)
                def limit(self, n): return replace(self, lim=int(n))

                def build(self):
                    if not self.table:
                        raise ValueError("no table")
                    sql, params = f"SELECT {', '.join(self.cols)} FROM {self.table}", []
                    if self.cond:
                        s, params = self.cond.render()
                        sql += f" WHERE {s}"
                    if self.order: sql += " ORDER BY " + ", ".join(self.order)
                    if self.lim is not None: sql += f" LIMIT {self.lim}"
                    return sql, params

            db = sqlite3.connect(":memory:")
            db.execute("CREATE TABLE users (name TEXT, age INT, city TEXT)")
            db.executemany("INSERT INTO users VALUES (?, ?, ?)",
                           [("ann", 34, "Pune"), ("bob", 19, "Delhi"), ("cy", 45, "Pune"), ("dee", 28, "Goa")])

            age, city, name = Col("age"), Col("city"), Col("name")
            base = Query().select("name", "age").from_("users")
            adults_in = base.where(age > 21).order_by("age")
            q1 = adults_in.where(city.in_(["Pune", "Goa"]))
            q2 = base.where((city == "Delhi") | ~(age < 40)).limit(5)
            evil = base.where(name == "x' OR '1'='1")

            for q in (q1, q2, evil):
                sql, params = q.build()
                print(sql, params, "->", db.execute(sql, params).fetchall())
            print("base query untouched:", base.build())
        '''),
        "The injection attempt returned nothing: the value travelled as a bound parameter, so the database compared <code>name</code> with that literal string. Immutability is why <code>adults_in</code> and <code>q1</code> could both be built from <code>base</code> without either changing it.",
    ],
    extend=[
        "Joins add a <code>joins</code> tuple of (table, condition). Dialects (Postgres <code>$1</code> placeholders, MySQL <code>%s</code>) are a rendering strategy. Identifiers (table and column names) cannot be parameters, so they are validated against an allow-list, as <code>Col</code> does here.",
    ],
    questions=[
        question(
            "Why make the builder immutable?",
            "medium",
            "Queries are often built from a shared base (&ldquo;active users&rdquo;) and specialised in different places. With a mutable builder, adding a <code>where</code> in one place silently changes the base for everyone else, a bug that is hard to see. Returning a new object from each method makes every intermediate query a safe, reusable value, at the cost of small copies.",
        ),
        question(
            "How does parameter binding prevent SQL injection?",
            "medium",
            "The SQL text with placeholders and the values are sent to the database separately; the database parses the text once and treats values strictly as data, never as SQL. A value like <code>x' OR '1'='1</code> is compared as a literal string. Concatenating values into the SQL string lets them change the query's structure, which is the injection.",
        ),
    ],
)


PLUGIN_SYSTEM = problem(
    id="plugin-system",
    title="Design a Plugin System",
    level="medium",
    patterns=["Factory", "Strategy", "Observer"],
    summary="Plugins register themselves, declare hooks they handle, are created from config, and are isolated from each other's failures.",
    statement=[
        "Design the extension mechanism for an application (an editor, a CI system, a data pipeline): third-party plugins add behaviour at defined hook points (on save, before build, transform record) without modifying the core. Which plugins run, and with what settings, comes from configuration.",
    ],
    requirements=[
        "Plugins self-register under a name. Configuration lists plugins and their options; the core instantiates them. Hooks are named; each plugin implements the hooks it cares about. One failing plugin must not break the others or the core. Plugins run in a defined order.",
    ],
    choose=[
        ["Create plugin objects from names in a config file", "Factory (registry)", "Name &rarr; class; plugins register via <code>__init_subclass__</code>"],
        ["Each plugin implements a common interface differently", "Strategy", "Hook methods with a shared signature"],
        ["Core announces hook points; plugins react", "Observer", "A hook call notifies every plugin implementing it"],
    ],
    classes=[
        ["<code>Plugin</code>", "Base class: registry, options, optional hook methods"],
        ["<code>PluginManager</code>", "Load from config, order by priority, call hooks with isolation"],
    ],
    implementation=[
        code('''
            class Plugin:
                registry = {}
                priority = 100

                def __init_subclass__(cls, name=None, **kw):
                    super().__init_subclass__(**kw)
                    Plugin.registry[name or cls.__name__.lower()] = cls

                def __init__(self, **options): self.options = options

            class TrimWhitespace(Plugin, name="trim"):
                priority = 10
                def on_save(self, text): return "\\n".join(l.rstrip() for l in text.splitlines())

            class AddHeader(Plugin, name="header"):
                def on_save(self, text): return f"# {self.options.get('text', 'generated')}\\n{text}"

            class WordLimit(Plugin, name="limit"):
                def on_save(self, text):
                    if len(text.split()) > self.options["max"]:
                        raise ValueError(f"more than {self.options['max']} words")
                    return text

            class Stats(Plugin, name="stats"):
                def on_open(self, text): return f"{len(text.split())} words"

            class Broken(Plugin, name="broken"):
                def on_save(self, text): return text.upper() / 2          # a buggy third-party plugin

            class PluginManager:
                def __init__(self, config):
                    self.plugins = []
                    for entry in config:
                        cls = Plugin.registry.get(entry["name"])
                        if cls is None:
                            print(f"  warning: unknown plugin {entry['name']!r} skipped")
                            continue
                        self.plugins.append(cls(**entry.get("options", {})))
                    self.plugins.sort(key=lambda p: p.priority)

                def pipeline(self, hook, value):
                    """each plugin transforms the value; failures are isolated"""
                    for p in self.plugins:
                        fn = getattr(p, hook, None)
                        if fn is None:
                            continue
                        try:
                            value = fn(value)
                        except Exception as e:
                            print(f"  plugin {type(p).__name__} failed in {hook}: {e!r}; skipped")
                    return value

                def collect(self, hook, value):
                    return [r for p in self.plugins if (fn := getattr(p, hook, None)) for r in [fn(value)]]

            config = [
                {"name": "header", "options": {"text": "notes"}},
                {"name": "trim"},
                {"name": "broken"},
                {"name": "limit", "options": {"max": 6}},
                {"name": "stats"},
                {"name": "spellcheck"},
            ]
            pm = PluginManager(config)
            print([type(p).__name__ for p in pm.plugins])
            print(repr(pm.pipeline("on_save", "buy milk   \\ncall bob  ")))
            print(pm.collect("on_open", "one two three"))
        '''),
        "The broken plugin raised, was reported and skipped, and every other plugin still ran; the unknown <code>spellcheck</code> entry was a warning, not a crash. Priorities put <code>trim</code> before <code>header</code> regardless of the order in the config.",
    ],
    extend=[
        "Third-party packages register through entry points (<code>importlib.metadata.entry_points(group=\"myapp.plugins\")</code>), which is how pytest and many CLIs discover plugins without importing them by name. Untrusted plugins need real isolation: a separate process with a timeout, because an exception handler cannot stop a plugin that loops forever or corrupts shared state.",
    ],
    questions=[
        question(
            "How do you keep a slow or crashing plugin from taking down the host?",
            "hard",
            "Exceptions: wrap each hook call, log and skip (as above), and disable a plugin after repeated failures. Slowness and hangs: run plugin hooks with a timeout, which in Python really means in a separate process or a worker pool you can abandon, since threads cannot be killed. Resource abuse and security: separate processes with limits, or a sandbox (WASM, containers). Define a narrow API for plugins so they cannot reach into core internals.",
        ),
        question(
            "Why register plugins with <code>__init_subclass__</code> instead of a manual list?",
            "medium",
            "Defining the class is enough to make it available; there is no second place to forget to update. The core never imports plugins by name, so plugins can live in separate packages. The trade-off is that registration happens at import time, so the plugin module must be imported (directly or via entry points) before the registry is read.",
        ),
    ],
)


DRAWING_APP = problem(
    id="drawing-app",
    title="Design a Drawing Application",
    level="hard",
    patterns=["Composite", "Prototype", "Command", "Observer"],
    summary="Shapes and groups, duplicate via prototypes, move/resize/delete as undoable commands, canvas listeners.",
    statement=[
        "Design the model of a vector drawing app (a mini Figma or Excalidraw): users add shapes, group them, duplicate shapes or groups, move and delete them, and undo any action. The canvas view redraws when the model changes.",
    ],
    requirements=[
        "Shapes: rectangle, circle (more later). Groups contain shapes and groups; moving a group moves everything inside. Duplicate creates an independent deep copy with a new id, offset slightly. Every user action is undoable. Bounding boxes work for shapes and groups.",
    ],
    choose=[
        ["Groups contain shapes and other groups", "Composite", "<code>move</code> and <code>bounds</code> work the same on a shape or a group"],
        ["Duplicate an arbitrary configured shape or group", "Prototype", "<code>clone()</code> deep-copies and assigns fresh ids"],
        ["Every action undoable", "Command", "Add, move, delete as commands on a history stack"],
        ["View redraws on changes", "Observer", "The document notifies listeners after each command"],
    ],
    classes=[
        ["<code>Shape</code>, <code>Rect</code>, <code>Circle</code>", "Leaves: position, size, <code>move</code>, <code>bounds</code>, <code>clone</code>"],
        ["<code>Group</code>", "Composite of shapes"],
        ["<code>AddCmd</code>, <code>MoveCmd</code>, <code>DeleteCmd</code>", "Commands with do/undo"],
        ["<code>Document</code>", "Top-level items, history, listeners"],
    ],
    implementation=[
        code('''
            import copy
            from itertools import count

            _ids = count(1)

            class Shape:
                def __init__(self, x, y): self.id, self.x, self.y = next(_ids), x, y
                def move(self, dx, dy): self.x += dx; self.y += dy
                def clone(self, dx=10, dy=10):                     # prototype
                    c = copy.deepcopy(self)
                    c._renumber(); c.move(dx, dy)
                    return c
                def _renumber(self): self.id = next(_ids)

            class Rect(Shape):
                def __init__(self, x, y, w, h): super().__init__(x, y); self.w, self.h = w, h
                def bounds(self): return (self.x, self.y, self.x + self.w, self.y + self.h)
                def __repr__(self): return f"Rect#{self.id}@({self.x},{self.y})"

            class Circle(Shape):
                def __init__(self, x, y, r): super().__init__(x, y); self.r = r
                def bounds(self): return (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)
                def __repr__(self): return f"Circle#{self.id}@({self.x},{self.y})"

            class Group(Shape):                                    # composite
                def __init__(self, *children):
                    self.id, self.children = next(_ids), list(children)
                def move(self, dx, dy):
                    for c in self.children: c.move(dx, dy)
                def bounds(self):
                    bs = [c.bounds() for c in self.children]
                    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))
                def _renumber(self):
                    self.id = next(_ids)
                    for c in self.children: c._renumber()
                def __repr__(self): return f"Group#{self.id}{self.children}"

            class AddCmd:
                def __init__(self, item): self.item = item
                def do(self, doc): doc.items.append(self.item)
                def undo(self, doc): doc.items.remove(self.item)

            class MoveCmd:
                def __init__(self, item, dx, dy): self.item, self.dx, self.dy = item, dx, dy
                def do(self, doc): self.item.move(self.dx, self.dy)
                def undo(self, doc): self.item.move(-self.dx, -self.dy)

            class DeleteCmd:
                def __init__(self, item): self.item, self.index = item, None
                def do(self, doc):
                    self.index = doc.items.index(self.item); doc.items.remove(self.item)
                def undo(self, doc): doc.items.insert(self.index, self.item)

            class Document:
                def __init__(self): self.items, self.history, self.listeners = [], [], []
                def run(self, cmd):
                    cmd.do(self); self.history.append(cmd); self._changed(type(cmd).__name__)
                def undo(self):
                    cmd = self.history.pop(); cmd.undo(self); self._changed("undo " + type(cmd).__name__)
                def _changed(self, why):
                    for fn in self.listeners: fn(why, self)

            doc = Document()
            doc.listeners.append(lambda why, d: print(f"  redraw after {why:16} items={d.items}"))
            r, c = Rect(0, 0, 40, 20), Circle(60, 10, 10)
            doc.run(AddCmd(r)); doc.run(AddCmd(c))
            g = Group(r, c)
            doc.items[:] = [g]                                   # group them (in a real app: a GroupCmd)
            doc.run(AddCmd(g.clone()))                           # duplicate the whole group
            doc.run(MoveCmd(g, 5, 5))
            print("group bounds:", g.bounds(), "| copy bounds:", doc.items[1].bounds())
            doc.run(DeleteCmd(g))
            doc.undo(); doc.undo()
            print("after two undos, original group back at:", g.bounds())
        '''),
        "The duplicate is fully independent: moving the original group did not move the copy, because <code>clone</code> deep-copied every child and gave each a new id. That independence is the point of Prototype here &mdash; shallow copies sharing children would make edits to one appear in the other.",
    ],
    extend=[
        "Grouping and ungrouping should be commands too (the demo sets <code>items</code> directly to keep it short). Real-time collaboration replaces the local history with operations sent to a server and transformed or merged (CRDTs). Rendering is a visitor over the composite: SVG export, hit-testing and snapping are more visitors.",
    ],
    questions=[
        question(
            "Why does <code>clone</code> need to renumber ids after <code>deepcopy</code>?",
            "medium",
            "<code>deepcopy</code> copies attribute values, including the id, so the copy would share identity with the original: selection, undo history and collaboration all key on ids and would confuse the two. Renumbering recursively (the group renumbers its children) gives every copied object a fresh identity while keeping all other properties.",
        ),
        question(
            "A user drags a shape and the app records 200 tiny MoveCmds. How do you fix undo?",
            "medium",
            "Coalesce: while a drag is in progress, update the shape directly (or merge consecutive moves of the same item into one command, as the text editor merges keystrokes), and push a single <code>MoveCmd</code> with the total offset when the mouse is released. One drag becomes one undo step, and history memory stays small.",
        ),
    ],
)

PROBLEMS = [DOC_EXPORT, EXPRESSION_EVALUATOR, HTTP_MIDDLEWARE, QUERY_BUILDER, PLUGIN_SYSTEM, DRAWING_APP]
