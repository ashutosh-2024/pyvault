"""Animations traced from real runs, one chapter per approach.

The hand-written generators in this package tell a story for one problem.
This module does the same job for every other problem by watching the code:
each approach is executed on its own tests under sys.settrace, one call of a
good size is picked, and every executed line becomes a frame showing the data
the code is working on -- arrays with their index pointers, grids, trees,
linked lists, graphs, tries and heaps -- plus the variables, the call stack
and the line that just ran. Nothing is typed by hand, so what the reader
watches is what the code did.

Scene frames (rendered by assets/js/viz.js):

frame:  {"caption": html, "line": int, "panels": [panel, ...],
         "vars": [[name, value, changed], ...], "stack": [str, ...]}
panel:  {"t": "arr",  "id", "label", "v": [str], "cls": [str], "ptr": {idx: [names]}, "keys"?: [str]}
        {"t": "grid", "id", "label", "v": [[str]], "cls": [[str]]}
        {"t": "net",  "id", "label", "nodes": [[key, text, x, y, cls, [tags]]],
                      "edges": [[key_a, key_b, cls, label]], "dir": bool}
chapter: {"title", "code", "frames"}
"""
from __future__ import annotations

import ast
import builtins
import contextlib
import html
import io
import re
import sys
import time
from collections import deque

MAX_FRAMES = 110         # frames per chapter (one per executed line)
MIN_EVENTS = 6           # a call this short is too trivial to prefer
MAX_SEGMENTS = 14        # calls to record before the tests are abandoned
DEADLINE = 6.0           # seconds of tracing per approach
MAX_ITEMS = 48           # longest list drawn as cells
MAX_NODES = 63           # largest tree / list / graph drawn
MAX_PANELS = 6
CELL_CHARS = 7

FILE = "<approach>"


class _Stop(BaseException):
    """Raised inside the traced program to abandon the remaining tests."""


# =================================================================== snapshot
# A snapshot turns live values into plain data at one instant, keyed by id() so
# identity (the same list or node reached through two names) survives.

SCALARS = (int, float, str, bool, type(None), complex, bytes)
LINK_ATTRS = ("left", "right", "next", "prev", "children", "child", "random", "parent", "down", "up", "neighbors")


def short(x, n=CELL_CHARS):
    """Display text for a scalar or a small tuple."""
    if isinstance(x, bool):
        s = "T" if x else "F"
    elif x is None:
        s = "·"
    elif isinstance(x, float):
        if x == float("inf"):
            s = "∞"
        elif x == float("-inf"):
            s = "-∞"
        elif x.is_integer():
            s = str(int(x))
        else:
            s = f"{x:.3g}"
    elif isinstance(x, str):
        s = x if x else "''"
    elif isinstance(x, (tuple, list)) and len(x) <= 4 and all(isinstance(y, SCALARS) for y in x):
        s = ",".join(short(y, 99) for y in x)
    else:
        s = str(x)
    return s if len(s) <= n else s[: n - 1] + "…"


def attrs(o):
    """Instance attributes, whether stored in __dict__ or __slots__."""
    d = getattr(o, "__dict__", None)
    out = dict(d) if d is not None else {}
    for cls in type(o).__mro__:
        for name in getattr(cls, "__slots__", ()) or ():
            if isinstance(name, str) and name not in out and not name.startswith("__") and hasattr(o, name):
                out[name] = getattr(o, name)
    return out


def is_node(o):
    if isinstance(o, SCALARS) or isinstance(o, (list, tuple, dict, set, frozenset, deque)):
        return False
    if isinstance(o, type) or callable(o) or type(o).__module__ not in ("__main__", "builtins"):
        return False
    d = attrs(o)
    if not d:
        return False
    if any(a in d for a in LINK_ATTRS):
        return True
    return "node" in type(o).__name__.lower()


def node_text(o):
    d = attrs(o)
    if "key" in d and "val" in d:
        return short(f"{short(d['key'], 4)}:{short(d['val'], 4)}")
    for a in ("val", "value", "data", "char", "ch", "key", "word"):
        if a in d and isinstance(d[a], SCALARS) and d[a] is not None:
            return short(d[a])
    return ""


def node_end(o):
    d = attrs(o)
    for a in ("is_end", "end", "is_word", "isEnd", "terminal", "word_end"):
        if d.get(a):
            return True
    return isinstance(d.get("word"), str) and bool(d.get("word"))


class Snap:
    """Plain-data copy of a set of variables. Nodes go into one shared table."""

    def __init__(self):
        self.nodes = {}            # oid -> {"text", "kind", "kids": [(slot, oid|None)], "extra": [(attr, oid)], "end"}
        self.keep = []             # hold refs so ids stay unique for the snapshot's lifetime

    def node(self, o):
        oid = id(o)
        if oid in self.nodes or len(self.nodes) >= 400:
            return oid
        self.keep.append(o)
        d = attrs(o)
        rec = {"text": node_text(o), "end": node_end(o), "kids": [], "extra": [], "kind": "list"}
        self.nodes[oid] = rec
        todo = []
        if "left" in d or "right" in d:
            rec["kind"] = "bin"
            for a in ("left", "right"):
                k = d.get(a)
                rec["kids"].append((a, id(k) if is_node(k) else None))
                if is_node(k):
                    todo.append(k)
        elif isinstance(d.get("neighbors"), list) or isinstance(d.get("adj"), list):
            rec["kind"] = "graph"
            for k in d.get("neighbors", d.get("adj")):
                if is_node(k):
                    rec["kids"].append(("", id(k)))
                    todo.append(k)
        elif isinstance(d.get("children"), (list, dict)):
            rec["kind"] = "nary"
            ch = d["children"]
            items = ch.items() if isinstance(ch, dict) else enumerate(ch)
            for lab, k in items:
                if is_node(k):
                    rec["kids"].append((str(lab) if isinstance(ch, dict) else "", id(k)))
                    todo.append(k)
        for a in ("next", "prev", "random", "child", "parent", "down", "up"):
            k = d.get(a)
            if is_node(k):
                rec["extra"].append((a, id(k)))
                todo.append(k)
        for k in todo:
            self.node(k)
        return oid

    def val(self, x, depth=0):
        if isinstance(x, SCALARS):
            return ("s", x)
        if is_node(x):
            return ("n", self.node(x))
        if depth > 3:
            return ("s", "…")
        if isinstance(x, (list, tuple, deque)):
            kind = "tuple" if isinstance(x, tuple) else "deque" if isinstance(x, deque) else "list"
            items = list(x)
            out = [self.val(y, depth + 1) for y in items[:MAX_ITEMS + 1]]
            self.keep.append(x)
            return ("l", kind, out, len(items), id(x))
        if isinstance(x, dict):
            self.keep.append(x)
            items = list(x.items())
            return ("d", [(self.val(k, depth + 1), self.val(v, depth + 1)) for k, v in items[:MAX_ITEMS + 1]],
                    len(items), id(x), type(x).__name__)
        if isinstance(x, (set, frozenset)):
            try:
                items = sorted(x)
            except TypeError:
                items = sorted(x, key=repr)
            return ("t", [self.val(y, depth + 1) for y in items[:MAX_ITEMS + 1]], len(items))
        d = attrs(x) if type(x).__module__ in ("__main__", "builtins", None) else None
        if d and not isinstance(x, type) and not callable(x) and not type(x).__name__.startswith("_"):
            return ("o", type(x).__name__, {k: self.val(v, depth + 1) for k, v in list(d.items())[:12]
                                             if not callable(v) and not k.startswith("__")})
        return ("s", type(x).__name__)


NODES = {}          # node table of the event being rendered


def ntext(oid):
    rec = NODES.get(oid)
    return f"({rec['text']})" if rec and rec["text"] else "node"


def plain(m):
    """A snapshot value back to a short string (for the variables strip)."""
    k = m[0]
    if k == "s":
        x = m[1]
        if isinstance(x, str):
            return repr(x) if len(x) <= 24 else repr(x[:22]) + "…"
        if x is None:
            return "None"
        return short(x, 24)
    if k == "n":
        return ntext(m[1])
    if k == "l":
        o, c = ("(", ")") if m[1] == "tuple" else ("[", "]")
        body = ", ".join(plain(y) for y in m[2][:8])
        return o + body + (", …" if m[3] > 8 else "") + c
    if k == "d":
        body = ", ".join(f"{plain(a)}: {plain(b)}" for a, b in m[1][:6])
        return "{" + body + (", …" if m[2] > 6 else "") + "}"
    if k == "t":
        return "{" + ", ".join(plain(y) for y in m[1][:8]) + (", …" if m[2] > 8 else "") + "}" if m[2] else "set()"
    if k == "o":
        return m[1]
    return "?"


def cell(m):
    """A snapshot value as the text of one cell."""
    if m[0] == "s":
        return short(m[1])
    if m[0] == "l" and m[3] == 0:
        return "[]" if m[1] != "tuple" else "()"
    if m[0] == "l" and m[3] <= 4 and all(y[0] == "s" for y in m[2]):
        return short(tuple(y[1] for y in m[2]))
    if m[0] == "n":
        rec = NODES.get(m[1])
        return short(rec["text"]) if rec and rec["text"] else "●"
    return short(plain(m))


# =================================================================== tracing
class Segment:
    def __init__(self, test_line, owner):
        self.test_line = test_line
        self.owner = owner
        self.events = []
        self.truncated = False
        self.calls = []


SAFE_FUNCS = {"len", "abs", "min", "max", "ord", "chr", "isinstance", "int", "str", "sum", "any", "all",
              "bool", "float", "divmod", "range", "sorted", "tuple", "list", "set", "zip", "enumerate",
              "reversed", "round", "pow"}
SAFE_METHODS = {"isalnum", "isdigit", "isalpha", "lower", "upper", "isspace", "isupper", "islower", "get",
                "startswith", "endswith", "keys", "values", "items", "count", "index", "find", "bit_length",
                "bit_count"}


def _safe(expr):
    for n in ast.walk(expr):
        if isinstance(n, (ast.NamedExpr, ast.Lambda, ast.Yield, ast.YieldFrom, ast.Await)):
            return False
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id in SAFE_FUNCS:
                continue
            if isinstance(f, ast.Attribute) and f.attr in SAFE_METHODS:
                continue
            return False
    return True


class Source:
    """The approach's code, with per-line facts the renderer needs."""

    def __init__(self, code):
        self.code = code
        self.lines = code.split("\n")
        self.conds = {}           # line -> compiled test expression (if/elif/while), with the names it reads
        tree = ast.parse(code)
        for n in ast.walk(tree):
            if isinstance(n, (ast.If, ast.While)) and _safe(n.test):
                names = sorted({x.id for x in ast.walk(n.test) if isinstance(x, ast.Name)} - set(dir(builtins)))
                self.conds[n.lineno] = (compile(ast.Expression(n.test), FILE, "eval"), names)
        # x[... i ...] -> i points into x
        self.index_vars = {}
        self.letter_keyed = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Subscript):
                base = _dotted(n.value)
                if base:
                    nm = _index_name(n.slice)
                    if nm:
                        self.index_vars.setdefault(base, set()).add(nm)
                    if any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "ord"
                           for x in ast.walk(n.slice)):
                        self.letter_keyed.add(base)
        # for i, x in enumerate(arr) / for i in range(len(arr)) -> i walks arr
        for n in ast.walk(tree):
            if isinstance(n, (ast.For, ast.comprehension)) and isinstance(n.iter, ast.Call) and isinstance(n.iter.func, ast.Name):
                f, args = n.iter.func.id, n.iter.args
                tgt = n.target.elts[0] if isinstance(n.target, ast.Tuple) and n.target.elts else n.target
                if not isinstance(tgt, ast.Name):
                    continue
                if f == "enumerate" and args and _dotted(args[0]):
                    self.index_vars.setdefault(_dotted(args[0]), set()).add(tgt.id)
                elif f == "range" and args:
                    for x in ast.walk(args[-1] if len(args) < 3 else args[1]):
                        if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "len" and x.args and _dotted(x.args[0]):
                            self.index_vars.setdefault(_dotted(x.args[0]), set()).add(tgt.id)
        # grid[r][c] -> (r, c) pairs
        self.grid_pairs = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Subscript):
                base = _dotted(n.value.value)
                r, c = n.value.slice, n.slice
                if base and isinstance(r, ast.Name) and isinstance(c, ast.Name):
                    self.grid_pairs.setdefault(base, set()).add((r.id, c.id))
        # ints the code works on bit by bit
        BIT_OPS = (ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift)
        self.bit_vars = []
        def note(x):
            for y in ast.walk(x):
                if isinstance(y, ast.Name) and y.id not in self.bit_vars:
                    self.bit_vars.append(y.id)
        for n in ast.walk(tree):
            if isinstance(n, ast.BinOp) and isinstance(n.op, BIT_OPS):
                note(n.left)
                if not isinstance(n.op, (ast.LShift, ast.RShift)):
                    note(n.right)
            elif isinstance(n, ast.AugAssign) and isinstance(n.op, BIT_OPS):
                note(n.target)
            elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Invert):
                note(n.operand)
            elif isinstance(n, ast.Assign) and isinstance(n.value, ast.BinOp) and isinstance(n.value.op, BIT_OPS):
                for t in n.targets:
                    note(t)
        # names handed to heapq
        self.heaps = set(re.findall(r"heap(?:push|pop|ify|replace|pushpop)(?:_max)?\(\s*([\w.]+)", code))
        # `for v in adj[u]` -> adj is an adjacency structure
        self.adjacency = set(re.findall(r"\bin\s+([\w.]+)\[[^\]]+\]\s*:", code))
        self.adjacency |= set(re.findall(r"\bfor\s+[\w, ()]+\s+in\s+([\w.]+)\[[^\]]+\]", code))

    def comment(self, line):
        if 1 <= line <= len(self.lines):
            s = self.lines[line - 1]
            m = re.search(r"#\s*(.+)$", s)
            if m and s.count('"') % 2 == 0 and s.count("'") % 2 == 0:
                return m.group(1).strip()
        return ""

    def text(self, line):
        if 1 <= line <= len(self.lines):
            s = self.lines[line - 1]
            return re.sub(r"\s+#.*$", "", s).strip()
        return ""


def _index_name(sl):
    """`a[i]`, `a[i + 1]`, `a[i - 1]` -> "i": a name that is clearly a position."""
    if isinstance(sl, ast.Name):
        return sl.id
    if isinstance(sl, ast.BinOp) and isinstance(sl.op, (ast.Add, ast.Sub)):
        if isinstance(sl.left, ast.Name) and isinstance(sl.right, ast.Constant):
            return sl.left.id
        if isinstance(sl.right, ast.Name) and isinstance(sl.left, ast.Constant) and isinstance(sl.op, ast.Add):
            return sl.right.id
    return None


def _dotted(n):
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        inner = _dotted(n.value)
        return inner + "." + n.attr if inner else None
    return None


class Tracer:
    def __init__(self, src, tests, deadline=DEADLINE):
        self.src = src
        self.tests_lines = tests.split("\n")
        self.segments = []
        self.seg = None
        self.stack = []           # live approach frames
        self.muted = False
        self.deadline = time.monotonic() + deadline
        self.skip_names = {"<lambda>", "<module>"}

    # -- the traced program's frames
    def frames_info(self):
        out = []
        for f in self.stack:
            out.append(f)
        return out

    def snapshot(self, kind, frame, arg=None):
        s = Snap()
        stack = []
        for f in self.stack:
            loc = {}
            for k, v in list(f.f_locals.items()):
                if k.startswith("__") or k.startswith(".") or isinstance(v, type) or (callable(v) and not is_node(v)) or k in ("random", "heapq", "bisect"):
                    continue
                if type(v).__name__ == "module":
                    continue
                loc[k] = s.val(v)
            co = f.f_code
            params = co.co_varnames[:co.co_argcount + co.co_kwonlyargcount]
            stack.append({"fn": co.co_name, "line": f.f_lineno, "locals": loc, "params": list(params)})
        ev = {"kind": kind, "line": frame.f_lineno, "stack": stack, "nodes": s.nodes}
        if kind == "return":
            ev["ret"] = s.val(arg)
        if kind == "line" and frame.f_lineno in self.src.conds:
            code, names = self.src.conds[frame.f_lineno]
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    val = eval(code, frame.f_globals, dict(frame.f_locals))
                ev["cond"] = (bool(val), [(nm, plain(s.val(frame.f_locals[nm]))) for nm in names
                                          if nm in frame.f_locals and isinstance(frame.f_locals[nm], SCALARS)])
            except Exception:
                pass
        return ev

    def record(self, kind, frame, arg=None):
        seg = self.seg
        if seg is None or self.muted:
            return
        if len(seg.events) >= MAX_FRAMES + 1:
            seg.truncated = True
            self.muted = True
            for f in self.stack:
                f.f_trace_lines = False
            return
        seg.events.append(self.snapshot(kind, frame, arg))

    # -- sys.settrace hooks
    def global_trace(self, frame, event, arg):
        if time.monotonic() > self.deadline:
            raise _Stop
        code = frame.f_code
        if code.co_filename != FILE or code.co_name in self.skip_names:
            return None
        if not self.stack:                         # a call from the tests: maybe a new segment
            caller = frame.f_back
            line = ""
            while caller is not None and caller.f_code.co_filename not in ("<tests>",):
                caller = caller.f_back
            nested = False
            if caller is not None and 1 <= caller.f_lineno <= len(self.tests_lines):
                raw = self.tests_lines[caller.f_lineno - 1]
                line = raw.strip()
                nested = raw[:1].isspace()
            owner = id(frame.f_locals["self"]) if "self" in frame.f_locals else None
            keep = self.seg is not None and owner is not None and self.seg.owner == owner and not self.muted
            if not keep:
                if self.seg is not None:
                    self.segments.append(self.seg)
                    if len(self.segments) >= MAX_SEGMENTS:
                        self.seg = None
                        raise _Stop
                self.seg = Segment(line, owner)
                self.seg.nested = nested
                self.muted = False
            elif line and (not self.seg.calls or self.seg.calls[-1] != line):
                pass
            if line and line not in self.seg.calls:
                self.seg.calls.append(line)
        self.stack.append(frame)
        if self.muted:
            frame.f_trace_lines = False
        self.record("call", frame)
        return self.local_trace

    def local_trace(self, frame, event, arg):
        if event == "line":
            self.record("line", frame)
        elif event == "return":
            self.record("return", frame, arg)
            if self.stack and self.stack[-1] is frame:
                self.stack.pop()
            if not self.stack and self.seg is not None and self.seg.owner is None:
                self.segments.append(self.seg)
                self.seg = None
                if len(self.segments) >= MAX_SEGMENTS:
                    raise _Stop
        return self.local_trace

    def finish(self):
        if self.seg is not None and self.seg.events:
            self.segments.append(self.seg)
            self.seg = None


def trace(head, code, tests):
    """Run head + code + tests with tracing; return (Source, [Segment])."""
    src = Source(code)
    t = Tracer(src, tests)
    ns = {"__name__": "__main__"}
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        exec(compile(head, "<prelude>", "exec"), ns)
        exec(compile(code, FILE, "exec"), ns)
        sys.settrace(t.global_trace)
        try:
            exec(compile(tests, "<tests>", "exec"), ns)
        except _Stop:
            pass
        except Exception:
            pass
        finally:
            sys.settrace(None)
    t.finish()
    return src, [s for s in t.segments if s.events]


def literal(seg):
    """Was the call written out in the tests with its input (not a loop variable)?"""
    return any(re.search(r"\w\((?:[^()]*[\[\d\"'])", c) for c in seg.calls)


def pick(segments):
    """The most informative call that still fits in one chapter, preferring
    calls whose input is written out in the tests."""
    fits = [s for s in segments if not s.truncated and len(s.events) >= MIN_EVENTS]
    top = [s for s in fits if not getattr(s, "nested", False)]
    if top:                                        # written out in the tests, not drawn at random in a loop
        lit = [s for s in top if literal(s)]
        return max(lit or top, key=lambda s: len(s.events))
    lit = [s for s in fits if literal(s)]
    if lit:
        return max(lit, key=lambda s: len(s.events))
    if fits:
        return max(fits, key=lambda s: len(s.events))
    whole = [s for s in segments if not s.truncated]
    if whole:
        return max(whole, key=lambda s: len(s.events))
    return segments[0] if segments else None


# =================================================================== layout
def tree_layout(nodes, root, x0=0.0):
    """Binary trees by inorder position, n-ary trees with leaves left to right.
    Returns ({oid: (x, depth)}, tree_edges, extra_edges, width)."""
    pos, edges, extra = {}, [], []
    seen = set()
    counter = [x0]

    def bin_walk(oid, depth):
        seen.add(oid)
        rec = nodes[oid]
        kids = dict(rec["kids"]) if rec["kind"] == "bin" else {}
        l, r = kids.get("left"), kids.get("right")
        if l is not None and l not in seen and l in nodes and len(seen) < MAX_NODES:
            edges.append((oid, l, "L"))
            bin_walk(l, depth + 1)
        elif l is not None:
            extra.append((oid, l, "left"))
        pos[oid] = (counter[0], depth)
        counter[0] += 1
        if r is not None and r not in seen and r in nodes and len(seen) < MAX_NODES:
            edges.append((oid, r, "R"))
            bin_walk(r, depth + 1)
        elif r is not None:
            extra.append((oid, r, "right"))

    def nary_walk(oid, depth):
        seen.add(oid)
        rec = nodes[oid]
        kids = [(lab, k) for lab, k in rec["kids"] if k is not None]
        xs = []
        for lab, k in kids:
            if k in seen or k not in nodes or len(seen) >= MAX_NODES:
                extra.append((oid, k, lab))
                continue
            edges.append((oid, k, lab))
            nary_walk(k, depth + 1)
            xs.append(pos[k][0])
        if xs:
            pos[oid] = ((xs[0] + xs[-1]) / 2, depth)
        else:
            pos[oid] = (counter[0], depth)
            counter[0] += 1

    (bin_walk if nodes[root]["kind"] == "bin" else nary_walk)(root, 0)
    for oid in list(pos):
        for attr, k in nodes[oid]["extra"]:
            if k in pos and attr != "parent":
                extra.append((oid, k, attr))
    return pos, edges, extra, counter[0] - x0


# =================================================================== rendering
POINTER_NAMES = re.compile(r"^(i|j|k|l|r|lo|hi|low|high|mid|m|left|right|start|end|begin|slow|fast|p|q|p1|p2|"
                           r"read|write|w|idx|index|pos|ptr|cur|curr|a|b|x|y|t|s|e|top|bottom|lt|gt|"
                           r"[a-z]{1,3}\d|[a-z_]*_(i|idx|ptr|index))$")
WINDOW_BOUNDS = {"lo", "hi", "low", "high", "left", "right", "l", "r", "start", "end", "begin"}
STRONG_POINTERS = {"lo", "hi", "low", "high", "left", "right", "l", "r", "i", "j", "start", "end", "slow", "fast"}


def esc(s):
    return html.escape(str(s), quote=False)


def code(s):
    return f"<code>{esc(s)}</code>"


class Renderer:
    def __init__(self, src, seg):
        self.src = src
        self.seg = seg
        # one bit width for the whole chapter, so columns never shift
        top = 0
        for ev in seg.events:
            for f in ev["stack"]:
                for k, v in f["locals"].items():
                    if k in src.bit_vars and v[0] == "s" and isinstance(v[1], int) and not isinstance(v[1], bool):
                        top = max(top, (v[1] if v[1] >= 0 else v[1] & 0xFFFFFFFF).bit_length())
        self.bit_width = 0 if not top else min(32, max(8, -(-top // 4) * 4))
        self.prev_cells = {}           # panel id -> list/grid of values in the previous frame
        self.visited_nodes = set()     # nodes that were ever the current one
        self.list_pos = {}             # linked-list node -> (x, y), fixed for the chapter
        self.list_rows = 0
        self.graph_pos = {}            # panel id -> {node label: (x, y)}
        self.panel_order = []

    # ---- variables of the frame being shown: outer frames first, inner wins
    def scope(self, ev):
        merged, origin = {}, {}
        for i, f in enumerate(ev["stack"]):
            for k, v in f["locals"].items():
                if k == "self" and v[0] == "o":
                    for a, av in v[2].items():
                        merged["self." + a] = av
                        origin["self." + a] = i
                    continue
                merged[k] = v
                origin[k] = i
        return merged

    def ints(self, scope):
        return {k: v[1] for k, v in scope.items() if v[0] == "s" and isinstance(v[1], int) and not isinstance(v[1], bool)}

    # ---- panels
    def panels(self, ev, scope):
        nodes = ev["nodes"]
        self.inner = ev["stack"][-1]["locals"] if ev["stack"] else {}
        ints = self.ints(scope)
        out = []
        node_tags = {}
        container_nodes = set()
        frames = ev["stack"]
        for depth, f in enumerate(frames):
            inner = depth == len(frames) - 1
            for k, v in f["locals"].items():
                if v[0] == "n":
                    if inner:
                        if k not in node_tags.setdefault(v[1], []):
                            node_tags[v[1]].append(k)
                    elif v[1] not in node_tags:
                        container_nodes.add(v[1])        # held by a caller further up the stack
                elif k == "self" and v[0] == "o":
                    for a, av in v[2].items():
                        if av[0] == "n" and "self." + a not in node_tags.setdefault(av[1], []):
                            node_tags[av[1]].append("self." + a)
        for k, v in scope.items():
            if v[0] == "n":
                continue
            elif v[0] == "l":
                for y in v[2]:
                    if y[0] == "n":
                        container_nodes.add(y[1])
                    elif y[0] == "l":
                        for z in y[2]:
                            if z[0] == "n":
                                container_nodes.add(z[1])
            elif v[0] == "d":
                for a, b in v[1]:
                    if b[0] == "n":
                        container_nodes.add(b[1])

        # -- node structures: trees and linked lists
        container_nodes -= set(node_tags)
        referenced = set(node_tags) | container_nodes
        if referenced:
            out += self.node_panels(nodes, referenced, node_tags, container_nodes)

        # -- containers
        for name, v in scope.items():
            if v[0] == "l":
                out += self.list_panels(name, v, scope, ints)
            elif v[0] == "d":
                out += self.dict_panels(name, v, scope, ints)
            elif v[0] == "t" and 0 < v[2] <= MAX_ITEMS and name not in self.src.adjacency:
                vals = [cell(y) for y in v[1]]
                out.append(self.arr(name, f"{name} (set)", vals, keys=None, noidx=True))
            elif v[0] == "s" and isinstance(v[1], str) and 1 < len(v[1]) <= MAX_ITEMS and name in self.src.index_vars:
                out.append(self.arr(name, name, [short(ch) for ch in v[1]], ptr=self.pointers(name, len(v[1]), ints)))
        if self.bit_width:
            rows = [(k, v) for k, v in ints.items() if k in self.src.bit_vars]
            if rows:
                out.insert(0, self.bits(rows))
        pointed = {n for p in out if p["t"] == "arr" for ns in p.get("ptr", {}).values() for n in ns}
        for lo, hi in (("lo", "hi"), ("low", "high"), ("left", "right"), ("l", "r")):
            if lo in ints and hi in ints and lo not in pointed and hi not in pointed:
                keys = [lo] + (["mid"] if "mid" in ints else []) + [hi]
                out.append(self.arr("range:" + lo, "search range", [short(ints[k]) for k in keys], keys=keys))
                break
        if not any(p["t"] == "grid" and p["id"] != "@bits" for p in out):
            coords = self.coord_grid(scope)
            if coords:
                out = [p for p in out if not (p["id"] in coords["sources"])] + [coords["panel"]]
        if not out:                          # strings the code rebuilds as it goes
            for name, v in scope.items():
                if v[0] == "s" and isinstance(v[1], str) and 2 <= len(v[1]) <= MAX_ITEMS:
                    out.append(self.arr(name, name, [short(ch) for ch in v[1]]))
        return out

    def coord_grid(self, scope):
        """Sets of (row, col) pairs drawn on the smallest grid that holds them."""
        def pairs(v):
            ms = v[1] if v[0] == "t" else v[2] if v[0] == "l" else []
            got = []
            for m in ms:
                if m[0] == "l" and m[3] == 2 and all(z[0] == "s" and isinstance(z[1], int) and not isinstance(z[1], bool) for z in m[2]):
                    got.append((m[2][0][1], m[2][1][1]))
                else:
                    return None
            return got
        sets, current = {}, []
        for k, v in scope.items():
            if v[0] == "t" and v[2]:
                ps = pairs(v)
                if ps:
                    sets[k] = ps
            elif v[0] == "l" and v[1] == "tuple" and v[3] == 2 and all(z[0] == "s" and isinstance(z[1], int) and not isinstance(z[1], bool) for z in v[2]):
                current.append((k, (v[2][0][1], v[2][1][1])))
        if not sets:
            return None
        allp = [q for ps in sets.values() for q in ps] + [q for _, q in current]
        if not hasattr(self, "_coord_box"):
            self._coord_box = None
        r0, c0 = min(q[0] for q in allp), min(q[1] for q in allp)
        r1, c1 = max(q[0] for q in allp), max(q[1] for q in allp)
        if self._coord_box:
            a, b, c, d = self._coord_box
            r0, c0, r1, c1 = min(r0, a), min(c0, b), max(r1, c), max(c1, d)
        if r1 - r0 > 14 or c1 - c0 > 16:
            return None
        self._coord_box = (r0, c0, r1, c1)
        rows, cols = r1 - r0 + 1, c1 - c0 + 1
        vals = [["" for _ in range(cols)] for _ in range(rows)]
        cls = [["" for _ in range(cols)] for _ in range(rows)]
        for k, ps in sets.items():
            for r, c in ps:
                cls[r - r0][c - c0] = "path"
        for k, (r, c) in current:
            if r0 <= r <= r1 and c0 <= c <= c1:
                cls[r - r0][c - c0] = "cur"
                vals[r - r0][c - c0] = k[:4]
        label = " / ".join(sets) + " (as cells)"
        return {"sources": set(sets), "panel": {"t": "grid", "id": "@cells", "label": label, "v": vals, "cls": cls,
                "rowLabels": [str(r) for r in range(r0, r1 + 1)], "colLabels": [str(c) for c in range(c0, c1 + 1)]}}

    def bits(self, rows):
        w = self.bit_width
        vals, cls, labels = [], [], []
        prev = self.prev_cells.get("@bits", {})
        for k, x in rows:
            u = x & ((1 << w) - 1) if x < 0 else x
            b = [str(u >> i & 1) for i in range(w - 1, -1, -1)]
            old = prev.get(k)
            vals.append(b)
            cls.append(["cur" if old is not None and old[i] != b[i] else ("yes" if b[i] == "1" else "")
                        for i in range(w)])
            labels.append(f"{k}={short(x, 11)}")
        self.prev_cells["@bits"] = {k: v for (k, _), v in zip(rows, vals)}
        return {"t": "grid", "id": "@bits", "label": "bits", "v": vals, "cls": cls, "rowLabels": labels,
                "colLabels": [str(i) for i in range(w - 1, -1, -1)]}

    def arr(self, pid, label, vals, ptr=None, keys=None, noidx=False, base=""):
        prev = self.prev_cells.get(pid)
        cls = []
        for i, x in enumerate(vals):
            if prev is not None and (i >= len(prev) or prev[i] != x):
                cls.append("cur")
            else:
                cls.append(base)
        if ptr:
            for i in ptr:
                i = int(i)
                if 0 <= i < len(cls) and cls[i] != "cur":
                    cls[i] = "src"
        self.prev_cells[pid] = list(vals)
        p = {"t": "arr", "id": pid, "label": label, "v": vals, "cls": cls}
        if ptr:
            p["ptr"] = {str(k): v for k, v in ptr.items()}
        if keys is not None:
            p["keys"] = keys
        if noidx:
            p["noidx"] = True
        return p

    def pointers(self, name, n, ints):
        names = set(self.src.index_vars.get(name, set()))
        if names:                         # the code indexes this array by name: window bounds are pointers too
            names |= {v for v in ints if v in WINDOW_BOUNDS}
        ptr = {}
        for var in sorted(names):
            if var in ints and POINTER_NAMES.match(var) and -1 <= ints[var] <= n:
                i = ints[var]
                if i == n:               # one past the end: draw it on the last slot's right
                    ptr.setdefault(n, []).append(var)
                elif i >= 0:
                    ptr.setdefault(i, []).append(var)
        return ptr

    def list_panels(self, name, v, scope, ints):
        items, n = v[2], v[3]
        if v[1] == "tuple" and n <= 4 and all(y[0] == "s" for y in items):
            return []
        if n == 0:
            return [self.arr(name, name, [], noidx=True)]
        if n > MAX_ITEMS:
            return []
        if all(y[0] == "n" for y in items):                # nodes waiting in a stack / queue
            return [self.arr(name, name + (" (deque)" if v[1] == "deque" else ""), [cell(y) for y in items], base="stack")]
        flat = all(y[0] == "s" or (y[0] == "l" and y[3] <= 4 and all(z[0] == "s" for z in y[2])) for y in items)
        rect = all(y[0] == "l" and all(z[0] == "s" for z in y[2]) for y in items) and n <= 16 \
            and 0 < max(y[3] for y in items) <= 20 and len({y[3] for y in items}) == 1
        is_grid_name = name in self.src.grid_pairs or not flat
        if rect and (is_grid_name or any(y[3] > 4 for y in items)):
            return [self.grid(name, items, scope, ints)]
        if not flat:
            if all(y[0] == "l" for y in items):              # ragged rows: one row of joined strings
                vals = [short(plain(y), 9) for y in items]
                return [self.arr(name, name, vals)]
            return []
        vals = [cell(y) for y in items]
        label = name + (" (deque)" if v[1] == "deque" else "")
        if name in self.src.letter_keyed and n in (26, 52, 128):
            base = 65 if re.search(r"-\s*65\b|ord\(\s*['\"]A['\"]\s*\)", self.src.code) else 97 if n == 26 else 0
            keys = [chr(base + i) if 32 < base + i < 127 else str(i) for i in range(n)]
            return [self.arr(name, label, vals, keys=keys)]
        panels = [self.arr(name, label, vals, ptr=self.pointers(name, n, ints))]
        if name in self.src.heaps and n > 1:
            panels.append(self.heap_tree(name, vals, panels[0]["cls"]))
        if re.search(r"(^|\.)(parent|par|root|roots|leader|boss|p|uf)$", name) and all(
                y[0] == "s" and isinstance(y[1], int) and 0 <= y[1] < n for y in items):
            panels.append(self.forest(name, [y[1] for y in items]))
        return panels

    def grid(self, name, rows, scope, ints):
        vals = [[cell(z) for z in y[2]] for y in rows]
        prev = self.prev_cells.get(name)
        cls = [["" for _ in r] for r in vals]
        marked = set()
        for k, v in scope.items():                           # sets / queues of (r, c) cells
            if k == name:
                continue
            members = v[1] if v[0] == "t" else v[2] if v[0] == "l" else [a for a, _ in v[1]] if v[0] == "d" else []
            for m in members:
                if m[0] == "l" and m[3] == 2 and all(z[0] == "s" and isinstance(z[1], int) for z in m[2]):
                    r, c = m[2][0][1], m[2][1][1]
                    if 0 <= r < len(vals) and 0 <= c < len(vals[r]):
                        cls[r][c] = "stack" if v[0] == "l" else "path"
                        marked.add((r, c))
        for r, row in enumerate(vals):
            for c, x in enumerate(row):
                if prev is not None and r < len(prev) and c < len(prev[r]) and prev[r][c] != x:
                    cls[r][c] = "cur"
        for rv, cv in self.src.grid_pairs.get(name, ()):
            if rv in ints and cv in ints:
                r, c = ints[rv], ints[cv]
                if 0 <= r < len(vals) and 0 <= c < len(vals[r]) and cls[r][c] != "cur":
                    cls[r][c] = "src"
        for k, v in scope.items():                           # a current (r, c) tuple
            if v[0] == "l" and v[1] == "tuple" and v[3] == 2 and all(z[0] == "s" and isinstance(z[1], int) for z in v[2]):
                r, c = v[2][0][1], v[2][1][1]
                if 0 <= r < len(vals) and 0 <= c < len(vals[r]) and k not in (name,):
                    cls[r][c] = "src"
        self.prev_cells[name] = [r[:] for r in vals]
        return {"t": "grid", "id": name, "label": name, "v": vals, "cls": cls}

    def dict_panels(self, name, v, scope, ints):
        items, n = v[1], v[2]
        if n > MAX_ITEMS:
            return []
        # a trie made of plain dicts
        if any(b[0] == "d" for a, b in items) and all(b[0] == "d" or (a[0] == "s" and str(a[1]) in ("$", "#", "*", "end", "word", "is_end", "$word")) for a, b in items):
            return [self.dict_trie(name, v)]
        # an adjacency map
        if name in self.src.adjacency and n <= 24 and all(b[0] in ("l", "t") for a, b in items):
            return [self.graph(name, [(a, b) for a, b in items], scope, ints)]
        if all(b[0] == "n" for a, b in items) and n:
            keys = [cell(a) for a, _ in items]
            vals = [cell(b) for _, b in items]
            return [self.arr(name, name, vals, keys=keys)]
        keys = [cell(a) for a, _ in items]
        vals = [cell(b) for _, b in items]
        return [self.arr(name, name + (f" ({v[4]})" if v[4] not in ("dict",) else ""), vals, keys=keys)]

    # ---- node-link structures
    def node_panels(self, nodes, referenced, tags, in_containers):
        # roots: reachable nodes that no other reachable node points to (as a child or next)
        reach, todo = set(), [r for r in referenced if r in nodes]
        while todo:
            o = todo.pop()
            if o in reach or o not in nodes:
                continue
            reach.add(o)
            for _, k in nodes[o]["kids"]:
                if k is not None:
                    todo.append(k)
            for a, k in nodes[o]["extra"]:
                if a in ("next", "child", "down"):
                    todo.append(k)
        pointed = set()
        for o in reach:
            for _, k in nodes[o]["kids"]:
                pointed.add(k)
            for a, k in nodes[o]["extra"]:
                if a in ("next", "child", "down"):
                    pointed.add(k)
        graph_nodes = [o for o in reach if nodes[o]["kind"] == "graph"]
        roots = [o for o in reach if o not in pointed]
        trees = [o for o in roots if nodes[o]["kind"] in ("bin", "nary")]
        lists = [o for o in reach if nodes[o]["kind"] == "list"]
        out = []
        cur_nodes = {o for o in tags if o in nodes}
        if trees:
            # stable order: the biggest tree first
            sizes = {}
            for t in trees:
                pos, _, _, w = tree_layout(nodes, t)
                sizes[t] = len(pos)
            trees.sort(key=lambda t: -sizes[t])
            for i, t in enumerate(trees[:2]):
                out.append(self.tree_panel(f"tree{i}", "tree" if i == 0 else "tree (second)", nodes, t, tags, in_containers))
        if lists:
            out.append(self.list_panel(nodes, lists, tags, in_containers))
        if graph_nodes:
            out.append(self.node_graph(nodes, graph_nodes, tags, in_containers))
        self.visited_nodes |= cur_nodes
        return out

    def node_cls(self, o, tags, in_containers, end=False):
        if o in tags:
            return "cur"
        if o in in_containers:
            return "stack"
        if end:
            return "answer"
        if o in self.visited_nodes:
            return "done"
        return ""

    def tree_panel(self, pid, label, nodes, root, tags, in_containers):
        pos, edges, extra, _ = tree_layout(nodes, root)
        out_nodes = []
        letter = {b: lab for a, b, lab in edges if nodes[a]["kind"] == "nary" and lab}
        for o, (x, d) in pos.items():
            rec = nodes[o]
            text = rec["text"] or letter.get(o, "")
            out_nodes.append([f"n{o}", text, x, d * 1.25, self.node_cls(o, tags, in_containers, rec["end"]),
                              tags.get(o, [])])
        out_edges = [[f"n{a}", f"n{b}", "", lab if nodes[a]["kind"] == "nary" and nodes[b]["text"] else ""]
                     for a, b, lab in edges]
        out_edges += [[f"n{a}", f"n{b}", "alt", attr if attr not in ("left", "right") else attr] for a, b, attr in extra
                      if b in pos]
        return {"t": "net", "id": pid, "label": label, "nodes": out_nodes, "edges": out_edges, "dir": False}

    def list_panel(self, nodes, lists, tags, in_containers):
        # chains in the order their heads are first met; positions never move
        heads = [o for o in lists if not any(k == o for p in lists for a, k in nodes[p]["extra"] if a == "next")]
        ordered = []
        seen = set()
        for h in sorted(heads, key=lambda o: self.list_pos.get(o, (99, 99))[::-1]) + lists:
            o = h
            while o is not None and o in nodes and o not in seen and len(seen) < MAX_NODES:
                seen.add(o)
                ordered.append(o)
                nxt = [k for a, k in nodes[o]["extra"] if a == "next"]
                o = nxt[0] if nxt else None
        doubly = any(a == "prev" for o in ordered for a, _ in nodes[o]["extra"])
        if doubly:                       # keep the list in its current order: nodes slide when relinked
            self.list_pos = {}
            row, col = 0, 0
            for o in ordered:
                prevs = [p for p in ordered if any(a == "next" and k == o for a, k in nodes[p]["extra"])]
                if prevs and prevs[0] in self.list_pos:
                    px, py = self.list_pos[prevs[0]]
                    if (px + 1, py) not in self.list_pos.values():
                        self.list_pos[o] = (px + 1, py)
                        continue
                if self.list_pos:
                    row += 1
                self.list_pos[o] = (0, row)
        for o in ordered:
            if o in self.list_pos:
                continue
            prev = [p for p in ordered if any(a == "next" and k == o for a, k in nodes[p]["extra"]) and p in self.list_pos]
            if prev:
                px, py = self.list_pos[prev[0]]
                taken = {v for v in self.list_pos.values()}
                if (px + 1, py) not in taken:
                    self.list_pos[o] = (px + 1, py)
                    continue
            row = self.list_rows
            self.list_rows += 1
            self.list_pos[o] = (0, row)
        out_nodes, out_edges = [], []
        for o in ordered:
            x, y = self.list_pos[o]
            out_nodes.append([f"n{o}", nodes[o]["text"], x * 1.7, y * 1.3, self.node_cls(o, tags, in_containers),
                              tags.get(o, [])])
            for a, k in nodes[o]["extra"]:
                if k not in seen:
                    continue
                back = any(a2 == "prev" and k2 == o for a2, k2 in nodes[k]["extra"])
                if a == "next":
                    out_edges.append([f"n{o}", f"n{k}", "both" if back else "", ""])
                elif a == "prev" and any(a2 == "next" and k2 == o for a2, k2 in nodes[k]["extra"]):
                    continue                                   # drawn as the two-headed next edge
                else:
                    out_edges.append([f"n{o}", f"n{k}", "alt", a])
        return {"t": "net", "id": "list", "label": "linked list", "nodes": out_nodes, "edges": out_edges, "dir": True}

    def node_graph(self, nodes, members, tags, in_containers):
        """Graph made of node objects (Node.neighbors): one ring per connected
        component, side by side, so an original and its copy sit apart."""
        import math
        order = self.graph_pos.setdefault("@nodes", {})
        for o in sorted(members, key=lambda o: order.get(o, 1e9)):
            order.setdefault(o, len(order))
        comp, comps = {}, []
        for o in sorted(members, key=order.get):
            if o in comp:
                continue
            cid, todo = len(comps), [o]
            comps.append([])
            while todo:
                x = todo.pop()
                if x in comp or x not in nodes:
                    continue
                comp[x] = cid
                comps[cid].append(x)
                todo += [k for _, k in nodes[x]["kids"] if k is not None]
                todo += [p for p in members if any(k == x for _, k in nodes[p]["kids"])]
        out_nodes, out_edges, x0, seen = [], [], 0.0, set()
        for c in comps:
            c.sort(key=order.get)
            n = len(c)
            R = 0 if n == 1 else max(1.0, n * 0.36)
            for i, o in enumerate(c):
                ang = -math.pi / 2 + 2 * math.pi * i / max(n, 1)
                out_nodes.append([f"n{o}", nodes[o]["text"], x0 + R + R * math.cos(ang), R + R * math.sin(ang),
                                  self.node_cls(o, tags, in_containers), tags.get(o, [])])
            x0 += 2 * R + 1.6
            for o in c:
                for _, k in nodes[o]["kids"]:
                    if k in comp and (k, o) not in seen:
                        seen.add((o, k))
                        out_edges.append([f"n{o}", f"n{k}", "", ""])
        return {"t": "net", "id": "nodegraph", "label": "graph", "nodes": out_nodes, "edges": out_edges, "dir": False}

    def dict_trie(self, name, v):
        nodes, counter = {}, [0]

        def add(m):
            oid = f"{name}:{counter[0]}"
            counter[0] += 1
            kids, end = [], False
            for a, b in m[1]:
                if b[0] == "d":
                    kids.append((cell(a), add(b)))
                else:
                    end = True
            nodes[oid] = {"text": "", "end": end, "kids": kids, "extra": [], "kind": "nary"}
            return oid

        root = add(v)
        pos, edges, _, _ = tree_layout(nodes, root)
        prev = self.prev_cells.get("trie:" + name, set())
        now = set(pos)
        letter = {b: lab for a, b, lab in edges}
        out_nodes = [[f"n{o}", letter.get(o, "·"), x, d * 1.25,
                      "cur" if o not in prev and prev else ("answer" if nodes[o]["end"] else ""), []]
                     for o, (x, d) in pos.items()]
        self.prev_cells["trie:" + name] = now
        out_edges = [[f"n{a}", f"n{b}", "", ""] for a, b, lab in edges]
        return {"t": "net", "id": "trie:" + name, "label": f"{name} (trie)", "nodes": out_nodes, "edges": out_edges,
                "dir": False, "edgeLabels": True}

    def heap_tree(self, name, vals, cls):
        nodes = {}
        for i in range(len(vals)):
            kids = [("left", 2 * i + 1 if 2 * i + 1 < len(vals) else None), ("right", 2 * i + 2 if 2 * i + 2 < len(vals) else None)]
            nodes[i] = {"text": vals[i], "end": False, "kids": kids, "extra": [], "kind": "bin"}
        pos, edges, _, _ = tree_layout(nodes, 0)
        out_nodes = [[f"h{i}", vals[i], x, d * 1.25, cls[i] if i < len(cls) else "", ["top"] if i == 0 else []]
                     for i, (x, d) in pos.items()]
        return {"t": "net", "id": "heap:" + name, "label": f"{name} drawn as a tree", "nodes": out_nodes,
                "edges": [[f"h{a}", f"h{b}", "", ""] for a, b, _ in edges], "dir": False, "mirror": name}

    def forest(self, name, parent):
        nodes = {i: {"text": str(i), "end": False, "kids": [], "extra": [], "kind": "nary"} for i in range(len(parent))}
        for i, p in enumerate(parent):
            if p != i:
                nodes[p]["kids"].append(("", i))
        roots = [i for i, p in enumerate(parent) if p == i]
        out_nodes, out_edges, x0 = [], [], 0.0
        for r in roots:
            pos, edges, _, w = tree_layout(nodes, r, x0)
            x0 += w + 0.6
            for o, (x, d) in pos.items():
                out_nodes.append([f"f{o}", str(o), x, d * 1.25, "answer" if o == r else "", []])
            out_edges += [[f"f{b}", f"f{a}", "", ""] for a, b, _ in edges]
        return {"t": "net", "id": "forest:" + name, "label": f"{name} as a forest", "nodes": out_nodes,
                "edges": out_edges, "dir": True}

    def graph(self, name, items, scope, ints):
        import math
        labels, edges = [], []
        def key(m):
            return cell(m)
        for a, b in items:
            labels.append(key(a))
        for a, b in items:
            nbrs = b[2] if b[0] == "l" else b[1]
            for m in nbrs:
                if m[0] == "l" and m[3] >= 1:
                    t, w = key(m[2][0]), (cell(m[2][1]) if m[3] > 1 else "")
                else:
                    t, w = key(m), ""
                if t not in labels:
                    labels.append(t)
                edges.append((key(a), t, w))
        pos = self.graph_pos.setdefault(name, {})
        for lab in labels:
            if lab not in pos:
                pos[lab] = None
        allk = list(pos)
        n = len(allk)
        R = max(1.6, n * 0.42)
        for i, lab in enumerate(allk):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            pos[lab] = (R + R * math.cos(ang), R * 0.82 + R * 0.82 * math.sin(ang))
        undirected = all((b, a, w) in edges for a, b, w in edges)
        seen_e, out_edges = set(), []
        for a, b, w in edges:
            k = tuple(sorted((a, b))) if undirected else (a, b)
            if k in seen_e:
                continue
            seen_e.add(k)
            out_edges.append([f"g{a}", f"g{b}", "", w])
        # node state from the other variables
        visited, waiting, current = set(), set(), {}
        for k, v in scope.items():
            if k == name:
                continue
            if v[0] == "t" and v[2] and all(cell(m) in pos for m in v[1]):
                visited |= {cell(m) for m in v[1]}
            elif v[0] == "l" and v[1] in ("deque", "list") and v[3] and all(m[0] == "s" and cell(m) in pos for m in v[2]):
                if not re.search(r"order|res|out|path|ans|result", k):
                    waiting |= {cell(m) for m in v[2]}
                else:
                    visited |= {cell(m) for m in v[2]}
        idx = self.src.index_vars.get(name, set())
        for loc in (self.inner, scope):
            for var in sorted(idx):
                if var in loc and loc[var][0] == "s" and cell(loc[var]) in pos:
                    current.setdefault(cell(loc[var]), []).append(var)
            if current:
                break
        out_nodes = []
        for lab in allk:
            x, y = pos[lab]
            cls = "cur" if lab in current else "stack" if lab in waiting else "done" if lab in visited else ""
            out_nodes.append([f"g{lab}", lab, x, y, cls, current.get(lab, [])])
        return {"t": "net", "id": "graph:" + name, "label": f"{name} (graph)", "nodes": out_nodes,
                "edges": out_edges, "dir": not undirected}

    # ---- the variables strip
    def variables(self, scope, prev_scope, shown):
        out = []
        for k, v in scope.items():
            if k in shown and v[0] != "s":
                continue
            if v[0] == "n":
                continue
            text = plain(v)
            old = prev_scope.get(k) if prev_scope is not None else None
            changed = prev_scope is not None and (old is None or plain(old) != text)
            out.append([k, text, 1 if changed else 0])
        return out


def node_text_of(m):
    return "●"


# =================================================================== captions
def describe_change(name, old, new, line=""):
    """One phrase for how a variable changed between two snapshots."""
    if old is None:
        return f"{code(name + ' = ' + plain(new))}"
    if old[0] == "l" and new[0] == "l":
        a, b = old[2], new[2]
        if new[3] == old[3] + 1 and b[:-1] == a[: len(b) - 1] and len(a) == old[3]:
            return f"{code(name)} gets {code(plain(b[-1]))} appended"
        front = re.search(rf"\b{re.escape(name)}\.(popleft|pop\(0\))", line)
        if new[3] == old[3] - 1 and a[1:] == b and front:
            return f"{code(plain(a[0]))} taken from the front of {code(name)}"
        if new[3] == old[3] - 1 and a[:-1] == b:
            return f"{code(plain(a[-1]))} popped off the end of {code(name)}"
        if new[3] == old[3] - 1 and a[1:] == b:
            return f"{code(plain(a[0]))} taken from the front of {code(name)}"
        if new[3] == old[3] + 1 and b[1:] == a:
            return f"{code(plain(b[0]))} pushed on the front of {code(name)}"
        if new[3] == old[3] and all(y[0] == "l" for y in a + b) and all(len(x[2]) == len(y[2]) for x, y in zip(a, b)):
            cells = [(r, c) for r in range(len(a)) for c in range(len(a[r][2])) if a[r][2][c] != b[r][2][c]]
            if len(cells) == 2:
                (r1, c1), (r2, c2) = cells
                if a[r1][2][c1] == b[r2][2][c2] and a[r2][2][c2] == b[r1][2][c1]:
                    return f"swap {code(f'{name}[{r1}][{c1}]')} and {code(f'{name}[{r2}][{c2}]')}"
            if 0 < len(cells) <= 3:
                return "; ".join(f"{code(f'{name}[{r}][{c}]')} becomes {code(plain(b[r][2][c]))}" for r, c in cells)
            if len(cells) == 4:
                return f"four cells of {code(name)} rotate"
        if new[3] == old[3]:
            diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
            if len(diff) == 1:
                i = diff[0]
                return f"{code(f'{name}[{i}]')} becomes {code(plain(b[i]))}"
            if len(diff) == 2 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]:
                return f"swap {code(f'{name}[{diff[0]}]')} and {code(f'{name}[{diff[1]}]')}"
        return f"{code(name)} is now {code(plain(new))}"
    if old[0] == "t" and new[0] == "t":
        added = [m for m in new[1] if m not in old[1]]
        gone = [m for m in old[1] if m not in new[1]]
        if len(added) == 1 and not gone:
            return f"{code(plain(added[0]))} added to {code(name)}"
        if len(gone) == 1 and not added:
            return f"{code(plain(gone[0]))} removed from {code(name)}"
    if old[0] == "d" and new[0] == "d":
        od = {plain(a): b for a, b in old[1]}
        nd = {plain(a): b for a, b in new[1]}
        ch = [k for k in nd if k not in od or plain(od[k]) != plain(nd[k])]
        gone = [k for k in od if k not in nd]
        if len(ch) == 1 and not gone:
            return f"{code(f'{name}[{ch[0]}] = {plain(nd[ch[0]])}')}"
        if len(gone) == 1 and not ch:
            return f"{code(gone[0])} removed from {code(name)}"
    return f"{code(name + ' = ' + plain(new))}"


def changes(prev_scope, scope, limit=4, line=""):
    if prev_scope is None:
        return []
    out = []
    for k, v in scope.items():
        old = prev_scope.get(k)
        if old is not None and plain(old) == plain(v) and old == v:
            continue
        if old is None and v[0] == "n":
            continue
        if v[0] == "n" or (old is not None and old[0] == "n"):
            if old is None or old != v:
                out.append(f"{code(k)} moves to {code(plain(v))}" if v[0] == "n" else describe_change(k, old, v, line))
            continue
        out.append(describe_change(k, old, v, line))
    if len(out) > limit:
        out = out[:limit] + ["…"]
    return out


def call_text(f):
    args = []
    params = f.get("params")
    for k, v in f["locals"].items():
        if k == "self" or (params is not None and k not in params):
            continue
        args.append(f"{k}={plain(v)}" if v[0] in ("s", "n") else k)
        if len(args) >= 4:
            break
    return f"{f['fn']}({', '.join(args)})"


# =================================================================== chapter
def chapter(title, ap, src, seg, statement_args=None):
    r = Renderer(src, seg)
    frames = []
    events = seg.events
    prev_scope = None
    test = "; ".join(seg.calls[:4]) + (" …" if len(seg.calls) > 4 else "")

    def frame_for(ev, caption, line):
        NODES.clear()
        NODES.update(ev["nodes"])
        scope = r.scope(ev)
        panels = r.panels(ev, scope)
        shown = {p["id"] for p in panels} | {p["id"].split(":", 1)[-1] for p in panels}
        f = {"caption": caption, "line": line, "panels": panels[:MAX_PANELS],
             "vars": r.variables(scope, prev_scope, shown),
             "stack": [call_text(s) for s in ev["stack"]] if len(ev["stack"]) > 1 else []}
        return f, scope

    first = events[0]
    NODES.clear()
    NODES.update(first["nodes"])
    if seg.owner is None and first["stack"]:
        f0 = first["stack"][0]
        args = ", ".join(f"{k}={plain(v) if v[0] != 'n' else ('tree' if NODES.get(v[1], {}).get('kind') in ('bin', 'nary') else 'list') + ' ' + plain(v)}"
                         for k, v in f0["locals"].items() if k != "self" and k in f0.get("params", [k]))
        cx = f"Input: {code(f0['fn'] + '(' + args + ')')}"
    else:
        cx = f"Running {code(test)}" if test else "Tracing one call from the tests"
    intro = (f"<strong>{esc(title)}</strong> &mdash; {ap['time']} time, {ap['space']} extra space. "
             f"{cx}. Step through to watch the code work on this input.")
    f, prev_scope = frame_for(first, intro, first["line"])
    frames.append(f)

    for k in range(1, len(events)):
        before, ev = events[k - 1], events[k]
        line = before["line"]
        text = src.text(line)
        bits = []
        depth_b, depth_e = len(before["stack"]), len(ev["stack"])
        if before["kind"] == "call":
            if len(before["stack"]) > 1:
                continue                     # the call frame of a nested call: shown by the line that made it
            continue
        if before["kind"] == "return":
            continue
        cap = code(text) if text else ""
        if "cond" in before:
            val, names = before["cond"]
            vals = ", ".join(f"{n} = {v}" for n, v in names[:4])
            cap += f" &rarr; <strong>{'true' if val else 'false'}</strong>" + (f" ({esc(vals)})" if vals else "")
        if ev["kind"] == "call" and depth_e > depth_b:
            bits.append(f"calls {code(call_text(ev['stack'][-1]))}")
        elif ev["kind"] == "return":
            if depth_e == 1:
                bits.append(f"returns {code(plain(ev['ret']))}")
            elif ev["stack"][-1]["fn"].startswith("<"):
                bits.append(f"yields {code(plain(ev['ret']))}")
            else:
                bits.append(f"{code(ev['stack'][-1]['fn'])} returns {code(plain(ev['ret']))} to {code(ev['stack'][-2]['fn'])}")
        NODES.clear()
        NODES.update(ev["nodes"])
        for b in before["nodes"]:
            NODES.setdefault(b, before["nodes"][b])
        scope_now = r.scope(ev)
        if depth_e == depth_b or ev["kind"] == "return":
            bits += changes(prev_scope, scope_now, line=text)
        com = src.comment(line)
        caption = cap
        if bits:
            caption += " &mdash; " + "; ".join(bits)
        if com:
            caption += f" <em>({esc(com)})</em>"
        f, prev_scope = frame_for(ev, caption, line)
        frames.append(f)

    last = events[-1]
    if seg.truncated:
        frames.append(frame_for(last, f"&hellip; and the run continues the same way. The first {len(frames)} steps "
                                f"are shown; this input needs more than that.", last["line"])[0])
    elif last["kind"] == "return" and len(last["stack"]) == 1:
        res = plain(last["ret"])
        frames[-1]["caption"] += f". <strong>Result: {esc(res)}</strong>"
        rv = last["ret"]
        if rv[0] in ("l", "d", "t") and not any(p["id"] == "result" for p in frames[-1]["panels"]):
            NODES.clear()
            NODES.update(last["nodes"])
            if rv[0] == "l" and rv[3] and all(y[0] == "s" or y[0] == "n" or y[0] == "l" for y in rv[2]) and rv[3] <= MAX_ITEMS:
                frames[-1]["panels"].append({"t": "arr", "id": "result", "label": "result",
                                             "v": [cell(y) for y in rv[2]], "cls": ["answer"] * rv[3]})
    return {"title": title, "code": ap["code"].rstrip("\n"), "frames": frames}


def plain_title(name):
    return html.unescape(re.sub(r"<[^>]+>", "", name)).strip()


def fallback_chapter(title, ap, why):
    lines = ap["code"].rstrip("\n").split("\n")
    return {"title": title, "code": ap["code"].rstrip("\n"), "frames": [{
        "caption": f"<strong>{esc(title)}</strong> &mdash; {ap['time']} time, {ap['space']} extra space. {why}",
        "line": 1, "panels": [], "vars": [], "stack": []}]}


def build_problem(job):
    """job: dict(id, head, tests, small_tests, approaches=[{name, code, small, time, space}])
    -> viz dict, or an error string."""
    chapters = []
    for ap in job["approaches"]:
        title = plain_title(ap["name"])
        tests = job["small_tests"] if ap.get("small") else job["tests"]
        try:
            src, segs = trace(job["head"], ap["code"], tests)
        except Exception as e:                                   # pragma: no cover
            chapters.append(fallback_chapter(title, ap, f"(could not trace: {esc(type(e).__name__)})"))
            continue
        seg = pick(segs)
        if seg is None:
            chapters.append(fallback_chapter(title, ap, "The tests never call this code directly, so there is nothing to trace."))
            continue
        chapters.append(chapter(title, ap, src, seg))
    return {"chapters": chapters}
