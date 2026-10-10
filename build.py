#!/usr/bin/env python3
"""Build the generated assets/js/*-data.js files from content/.

Every DSA solution is executed against its tests, and every code block in the
long-form sections is executed and its real output captured. If any of that
fails the build fails, which is the point: the site promises that what it
shows you actually happened.
"""
from __future__ import annotations

import hashlib
import json
import re
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "assets" / "js" / "data.js"
OUT_DSA = ROOT / "assets" / "js" / "dsa-data.js"
OUT_DEEP = ROOT / "assets" / "js" / "deepdive-data.js"
OUT_DB = ROOT / "assets" / "js" / "databases-data.js"
OUT_PREP = ROOT / "assets" / "js" / "prep-data.js"
OUT_SD = ROOT / "assets" / "js" / "systemdesign-data.js"
OUT_LLD = ROOT / "assets" / "js" / "lld-data.js"
OUT_SEARCH = ROOT / "assets" / "js" / "search-index.js"

TIMEOUT = 15
ENV = {
    **os.environ,
    "PYTHONHASHSEED": "0",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONIOENCODING": "utf-8",
    "COLUMNS": "80",
    "NO_COLOR": "1",
    "TERM": "dumb",
}


HEX_ADDR = re.compile(r"0x[0-9a-fA-F]{6,}")


def scrub(text: str, tmpdir: str, path: str, name: str) -> str:
    """Remove anything specific to this machine or this run."""
    text = text.replace(path, f"{name}.py")
    # macOS reports /private/var/... for a /var/... tempdir
    text = text.replace("/private" + tmpdir, ".").replace(tmpdir, ".")
    for prefix in {sys.prefix, sys.base_prefix,
                   str(pathlib.Path(sys.executable).parent.parent)}:
        text = text.replace(prefix, "<python>")
    # /private/var/... vs /var/... on macOS
    text = re.sub(r"/private(/var/folders/\S+)", r"\1", text)
    return HEX_ADDR.sub("0x...", text)


def run_snippet(name: str, src: str) -> tuple[str, bool]:
    """Run src as a script; return (combined output, raised?)."""
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / f"{name}.py"
        path.write_text(src, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True, text=True, env=ENV, cwd=td, timeout=TIMEOUT,
        )
    out = scrub(proc.stdout, td, str(path), name)
    err = scrub(proc.stderr, td, str(path), name)
    if err:
        out = (out + "\n" if out and not out.endswith("\n") else out) + err
    return out.rstrip("\n"), proc.returncode != 0


ALLOWED_TAGS = {"code", "strong", "em", "sup", "sub"}


DIFFS = {"easy", "medium", "hard"}


def make_starter(code: str, tests: str = "") -> str:
    """Signatures of the functions and classes the tests call, bodies replaced
    by `pass`: the scaffold the in-browser editor starts from, so the reader
    writes the same names the tests use. Private helpers are left out."""
    import ast
    import copy

    def stub(fn):
        fn = copy.deepcopy(fn)
        fn.body = [ast.Pass()]
        return fn

    used = set(re.findall(r"[A-Za-z_]\w*", tests)) if tests else None
    tree = ast.parse(code)
    keep = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            keep.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if used is None or node.name in used:
                keep.append(stub(node))
        elif isinstance(node, ast.ClassDef):
            if used is not None and node.name not in used:
                continue
            cls = copy.deepcopy(node)
            methods = [stub(n) for n in node.body
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                       and not (n.name.startswith("_") and not n.name.endswith("__"))]
            cls.body = methods or [ast.Pass()]
            keep.append(cls)
    parts = [ast.unparse(n) for n in keep]
    return "\n\n\n".join(parts) + "\n"


def check_viz(pid: str, v: dict, classes: set) -> dict:
    """Validate an animation produced by content/viz/ before shipping it."""
    def fail(msg):
        raise SystemExit(f"viz {pid}: {msg}")
    if not v.get("chapters"):
        fail("no chapters")
    for ci, ch in enumerate(v["chapters"]):
        if not ch.get("title") or not ch.get("frames"):
            fail(f"chapter {ci} needs a title and frames")
        for fi, fr in enumerate(ch["frames"]):
            where = f"chapter {ci} frame {fi}"
            if not fr.get("caption"):
                fail(f"{where}: no caption")
            for tag in re.findall(r"</?(\w+)", fr["caption"]):
                if tag not in ALLOWED_TAGS:
                    fail(f"{where}: unexpected <{tag}> in caption")
            if "panels" in fr:                       # traced frame (content/viz/auto.py)
                if "code" not in ch or not isinstance(fr.get("line"), int):
                    fail(f"{where}: traced frame needs the chapter's code and a line")
                for pn in fr["panels"]:
                    if pn["t"] == "arr":
                        if len(pn["v"]) != len(pn["cls"]) or set(pn["cls"]) - classes:
                            fail(f"{where}: bad array panel {pn['id']!r}")
                    elif pn["t"] == "grid":
                        if len(pn["v"]) != len(pn["cls"]) or {c for r in pn["cls"] for c in r} - classes:
                            fail(f"{where}: bad grid panel {pn['id']!r}")
                    elif pn["t"] == "net":
                        keys = {n[0] for n in pn["nodes"]}
                        if {n[4] for n in pn["nodes"]} - classes:
                            fail(f"{where}: unknown node classes in {pn['id']!r}")
                        if any(e[0] not in keys or e[1] not in keys for e in pn["edges"]):
                            fail(f"{where}: edge to a node not drawn in {pn['id']!r}")
                    else:
                        fail(f"{where}: unknown panel type {pn['t']!r}")
                continue
            g = fr.get("grid")
            if g:
                rows, cols = len(g["v"]), len(g["v"][0])
                if any(len(r) != cols for r in g["v"]) or len(g["cls"]) != rows \
                        or any(len(r) != cols for r in g["cls"]):
                    fail(f"{where}: ragged grid")
                bad = {c for r in g["cls"] for c in r} - classes
                if bad:
                    fail(f"{where}: unknown cell classes {bad}")
                for r1, c1, r2, c2 in fr.get("arrows", []):
                    if not (0 <= r1 < rows and 0 <= r2 < rows and 0 <= c1 < cols and 0 <= c2 < cols):
                        fail(f"{where}: arrow off the grid")
            a = fr.get("array")
            if a and (len(a["v"]) != len(a["cls"]) or set(a["cls"]) - classes):
                fail(f"{where}: bad array")
            if not g and not a:
                fail(f"{where}: nothing to draw")
    return v


VIZ_DIR = ROOT / "assets" / "viz"


MIN_EXAMPLES = 2          # worked examples per problem, each dry-run by every approach
MIN_POINTS = 8            # idea + steps + why pointers per approach
MIN_DRY = 3               # lines per dry run
MIN_FAQ = 3               # questions per approach


def explain_examples(entry: dict) -> list:
    """The worked examples of a write-up (content/explain/)."""
    return entry.get("examples") or []


def check_write_up(where: str, w: dict, n_examples: int) -> dict:
    """Validate one approach's write-up and return it in the shape problem.js renders."""
    def tags(part, text):
        for tag in re.findall(r"</?(\w+)", text):
            if tag not in ALLOWED_TAGS:
                raise SystemExit(f"{where}: unexpected <{tag}> in {part}")
    for part in ("idea", "steps", "why", "dry"):
        if not w.get(part):
            raise SystemExit(f"{where}: write-up has no {part!r}")
    if isinstance(w["dry"][0], str):
        raise SystemExit(f"{where}: 'dry' must be one list of lines per worked example")
    dry, faq = w["dry"], w.get("faq", [])
    points = len(w["idea"]) + len(w["steps"]) + len(w["why"])
    if points < MIN_POINTS:
        raise SystemExit(f"{where}: {points} pointers in idea/steps/why, want at least {MIN_POINTS}")
    if len(dry) != n_examples:
        raise SystemExit(f"{where}: {len(dry)} dry runs for {n_examples} worked examples")
    for k, run in enumerate(dry, 1):
        if len(run) < MIN_DRY:
            raise SystemExit(f"{where}: dry run {k} has {len(run)} lines, want at least {MIN_DRY}")
    if len(faq) < MIN_FAQ:
        raise SystemExit(f"{where}: {len(faq)} FAQ entries, want at least {MIN_FAQ}")
    for qa in faq:
        if len(qa) != 2 or not all(isinstance(x, str) and x for x in qa):
            raise SystemExit(f"{where}: an FAQ entry must be [question, answer]")
    for part in ("idea", "steps", "why"):
        for t in w[part]:
            tags(part, t)
    for run in dry:
        for t in run:
            tags("dry", t)
    for q, a in faq:
        tags("faq", q)
        tags("faq", a)
    return {"idea": w["idea"], "steps": w["steps"], "why": w["why"],
            "dry": dry, "faq": [list(qa) for qa in faq]}


def write_viz(pid: str, v: dict, name: str = "") -> dict:
    """Write one animation to assets/viz/<id>.json (fetched only when a reader opens
    it) and return the small stub stored on the problem."""
    VIZ_DIR.mkdir(exist_ok=True)
    body = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    name = name or pid
    (VIZ_DIR / f"{name}.json").write_text(body, encoding="utf-8")
    digest = hashlib.sha256(body.encode()).hexdigest()[:8]
    stub = {
        "src": f"assets/viz/{name}.json?v={digest}",
        "chapters": [c["title"] for c in v["chapters"]],
        "steps": [len(c["frames"]) for c in v["chapters"]],
        "examples": [c.get("example") for c in v["chapters"]],
        "frames": sum(len(c["frames"]) for c in v["chapters"]),
    }
    if all("code" in c for c in v["chapters"]):
        stub["traced"] = True                    # one chapter per approach, traced by content/viz/auto.py
    return stub


def trace_all(content, explain) -> dict:
    """Animations traced from real runs (content/viz/auto.py) for every problem,
    one chapter per approach, each on the write-up's worked examples where they
    fit. Runs in parallel."""
    from concurrent.futures import ProcessPoolExecutor
    from viz import auto
    jobs = []
    for topic in content.TOPICS:
        head = content.PRELUDE + "\n\n" + topic.get("prelude", "")
        for section in topic.get("sections", []):
            for prob in section["problems"]:
                jobs.append(dict(id=prob["id"], head=head, tests=prob["tests"],
                                 small_tests=prob.get("small_tests", ""),
                                 examples=explain_examples(explain.get(prob["id"], {})),
                                 approaches=[{k: ap.get(k) for k in ("name", "code", "small", "time", "space")}
                                             for ap in prob["approaches"]]))
    # cache by (tracer source, problem) so an unchanged problem is not traced again
    cache_dir = ROOT / ".viz-cache"
    cache_dir.mkdir(exist_ok=True)
    salt = hashlib.sha256(pathlib.Path(auto.__file__).read_bytes()).hexdigest()
    results, todo = {}, []
    for j in jobs:
        key = hashlib.sha256((salt + json.dumps(j, sort_keys=True)).encode()).hexdigest()[:20]
        f = cache_dir / f"{j['id']}-{key}.json"
        if f.exists():
            results[j["id"]] = json.loads(f.read_text(encoding="utf-8"))
        else:
            todo.append((j, f))
    if todo:
        with ProcessPoolExecutor() as pool:
            for (j, f), v in zip(todo, pool.map(auto.build_problem, [j for j, _ in todo], chunksize=4)):
                f.write_text(json.dumps(v, ensure_ascii=False), encoding="utf-8")
                results[j["id"]] = v
    live = {f"{j['id']}-{hashlib.sha256((salt + json.dumps(j, sort_keys=True)).encode()).hexdigest()[:20]}.json" for j in jobs}
    for f in cache_dir.glob("*.json"):
        if f.name not in live:
            f.unlink()
    return results


def build_dsa() -> int:
    """Execute every DSA solution against its tests and emit dsa-data.js."""
    import dsa as content
    import viz
    from explain import EXPLAIN
    viz_count = 0
    explained, unexplained = 0, []
    traced = trace_all(content, EXPLAIN)

    cache_path = ROOT / "content" / "leetcode.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    topics, total, checked = [], 0, 0
    for topic in content.TOPICS:
        sections, flat = [], []
        for section in topic.get("sections", []):
            problems = []
            for prob in section["problems"]:
                if prob["difficulty"] not in DIFFS:
                    raise SystemExit(f"{prob['id']}: bad difficulty {prob['difficulty']!r}")
                if not prob.get("tests"):
                    raise SystemExit(f"{prob['id']}: no tests, so nothing is verified")

                # --- LeetCode metadata, fetched once by fetch_leetcode.py
                meta, slug = {}, prob.get("slug")
                if slug:
                    if slug not in cache:
                        raise SystemExit(
                            f"{prob['id']}: {slug!r} missing from content/leetcode.json "
                            f"- run: python3 fetch_leetcode.py")
                    meta = cache[slug]
                    if meta["lc"] != prob["lc"]:
                        raise SystemExit(
                            f"{prob['id']}: lc={prob['lc']} but LeetCode says "
                            f"{meta['lc']} for {slug!r}")
                    if meta["difficulty"] != prob["difficulty"]:
                        raise SystemExit(
                            f"{prob['id']}: difficulty={prob['difficulty']!r} but "
                            f"LeetCode says {meta['difficulty']!r}")

                approaches = []
                head = content.PRELUDE + "\n\n" + topic.get("prelude", "")
                ex = EXPLAIN.get(prob["id"], {})
                ex_aps = ex.get("approaches", {})
                unknown = set(ex_aps) - {ap["name"] for ap in prob["approaches"]}
                if unknown:
                    raise SystemExit(f"{prob['id']}: write-up for unknown approach(es) {sorted(unknown)}")
                examples = explain_examples(ex)
                if ex_aps and len(examples) < MIN_EXAMPLES:
                    raise SystemExit(f"{prob['id']}: write-ups need {MIN_EXAMPLES} worked examples, "
                                     f"each with call and expect")
                for e in examples:
                    if not e.get("call") or "expect" not in e:
                        raise SystemExit(f"{prob['id']}: every worked example needs call and expect")
                check_example = "".join(
                    (e.get("setup", "") + "\n" +
                     f"__ex = ({e['call']})\n"
                     f"assert __ex == ({e['expect']}), "
                     f"'worked example {k} returned %r, the write-up says ' % (__ex,) + "
                     f"{e['expect']!r}\n")
                    for k, e in enumerate(examples, 1))
                for ap in prob["approaches"]:
                    # Exponential brute force can't run the full tests in time,
                    # so it is checked against the problem's smaller set.
                    tests = prob["tests"]
                    if ap.get("small"):
                        tests = prob.get("small_tests")
                        if not tests:
                            raise SystemExit(
                                f"{prob['id']} / {ap['name']}: small=True but no small_tests")
                    src = head + "\n\n" + ap["code"] + "\n\n" + tests + "\n" + \
                        (check_example if ap["name"] in ex_aps else "")
                    safe = re.sub(r"[^a-z0-9]+", "_",
                                  ap["name"].lower()).strip("_")[:40]
                    case = f"{prob['id'].replace('-', '_')}__{safe}"
                    out, raised = run_snippet(case, src)
                    if raised:
                        raise SystemExit(
                            f"\nDSA check failed: {prob['name']} / {ap['name']}\n{out}")
                    checked += 1
                    write_up = ex_aps.get(ap["name"])
                    if write_up:
                        write_up = check_write_up(f"{prob['id']} / {ap['name']}", write_up, len(examples))
                        explained += 1
                    else:
                        unexplained.append(f"{prob['id']} / {ap['name']}")
                    approaches.append({
                        "name": ap["name"],
                        "time": ap["time"],
                        "space": ap["space"],
                        "why": ap["why"],
                        "code": ap["code"].rstrip("\n"),
                        "best": bool(ap.get("best")),
                        "tag": ap.get("tag", ""),
                        "change": ap.get("change", ""),
                        "explain": write_up or None,
                    })

                total += 1
                best_ap = next((a for a in prob["approaches"] if a.get("best")),
                               prob["approaches"][-1])
                built = {
                    "id": prob["id"],
                    "starter": make_starter(best_ap["code"], prob["tests"]),
                    "num": total,
                    "lc": prob.get("lc"),
                    "slug": slug or "",
                    "url": f"https://leetcode.com/problems/{slug}/" if slug else "",
                    "premium": bool(meta.get("premium")),
                    "name": prob["name"],
                    "difficulty": prob["difficulty"],
                    "tags": prob.get("tags") or meta.get("tags", []),
                    "statement": prob.get("statement") or meta.get("statement", []),
                    "examples": prob.get("examples") or meta.get("examples", []),
                    "constraints": prob.get("constraints") or meta.get("constraints", []),
                    "note": prob.get("note", ""),
                    "pitfall": prob.get("pitfall", ""),
                    "approaches": approaches,
                    "recurrence": prob.get("recurrence"),
                    "tests": prob["tests"].rstrip("\n"),
                    "smallTests": prob.get("small_tests", "").rstrip("\n"),
                    "topic": topic["id"],
                    "topicTitle": topic["title"],
                    "section": section["id"],
                    "sectionTitle": section["title"],
                    "ref": ({"label": prob["ref"][0], "url": prob["ref"][1]}
                            if prob.get("ref") else None),
                    "worked": [{"call": e["call"], "setup": e.get("setup", ""), "expect": e["expect"]}
                                 for e in examples] if ex_aps else [],
                }
                expect = f"https://leetcode.com/problems/{slug}/" if slug else ""
                if built["url"] != expect:
                    raise SystemExit(
                        f"{prob['id']}: url {built['url']!r} does not match "
                        f"slug {slug!r}")
                rec = built["recurrence"]
                if rec and not (rec.get("state") and rec.get("formula")):
                    raise SystemExit(f"{prob['id']}: recurrence needs state and formula")
                if not built["statement"]:
                    raise SystemExit(
                        f"{prob['id']}: no statement. Premium or non-LeetCode "
                        f"problems must supply their own `statement=[...]`.")
                if prob["id"] in viz.REGISTRY:
                    built["vizIntro"] = write_viz(prob["id"], check_viz(prob["id"], viz.REGISTRY[prob["id"]](), viz.CELL_CLASSES),
                                                  name=f"{prob['id']}-intro")
                if prob["id"] in traced:
                    built["viz"] = write_viz(prob["id"], check_viz(prob["id"], traced[prob["id"]], viz.CELL_CLASSES))
                    if len(built["viz"]["chapters"]) != len(approaches):
                        raise SystemExit(f"{prob['id']}: {len(built['viz']['chapters'])} animation chapters "
                                         f"for {len(approaches)} approaches")
                    viz_count += 1
                problems.append(built)
                flat.append(built)
            sections.append({
                "id": section["id"],
                "title": section["title"],
                "summary": section.get("summary", ""),
                "idea": section.get("idea", []),
                "problems": problems,
            })
        topics.append({
            "id": topic["id"],
            "title": topic["title"],
            "status": topic.get("status", "ready"),
            "target": topic.get("target"),
            "layout": topic.get("layout", "flat"),
            "prelude": topic.get("prelude", "").strip("\n"),
            "sections": sections,
            "problems": flat,
            "count": len(flat),
        })

    body = json.dumps(topics, indent=2, ensure_ascii=False)
    OUT_DSA.write_text(
        "/* GENERATED FILE - do not edit by hand.\n"
        "   Source: content/dsa.py   Build: python3 build.py\n"
        "   Every solution below was executed against the problem's tests. */\n\n"
        f"window.GRAIL_PRELUDE = {json.dumps(content.PRELUDE.rstrip(), ensure_ascii=False)};\n"
        f"window.GRAIL_DSA = {body};\n",
        encoding="utf-8")
    for t in topics:
        if t["id"] in viz.REQUIRED_TOPICS:
            missing = [p["id"] for p in t["problems"] if "viz" not in p]
            if missing:
                raise SystemExit(f"{t['id']}: problems without an animation in content/viz/: {missing}")
    if unexplained:
        raise SystemExit(f"{len(unexplained)} approaches have no write-up in content/explain/: "
                         f"{unexplained[:10]}")
    print(f"built {len(topics)} DSA topics, {total} problems, "
          f"{checked} solutions executed, {explained} written up, {viz_count} animated "
          f"-> {OUT_DSA.relative_to(ROOT)}")
    return total


DEEP_TAGS = ALLOWED_TAGS | {"br"}
DEEP_LEVELS = {"medium", "hard"}
TOPIC_LEVELS = {"easy", "medium", "hard"}
DEEP_MAX_LINES = 45


def build_longform(package: str, out: pathlib.Path, var: str, name: str) -> int:
    """Execute every code block of a long-form section (Deep Dive, Databases)
    and emit its data file. Both share the schema in content/deepdive/_blocks.py."""
    import importlib
    content = importlib.import_module(package)

    topics, seen, runs = [], set(), 0
    problems = []

    def render(blocks, where, slug):
        nonlocal runs
        out = []
        for i, b in enumerate(blocks):
            if isinstance(b, str):
                for tag in re.findall(r"</?(\w+)", b):
                    if tag not in DEEP_TAGS:
                        problems.append(f"{where}: unexpected <{tag}>")
                out.append({"type": "p", "html": b})
                continue
            b = dict(b)
            if b["type"] == "code":
                if b.pop("run"):
                    output, raised = run_snippet(f"{slug}_{i}", b["src"])
                    runs += 1
                    if raised != b["raises"]:
                        what = "unexpected traceback" if raised else "expected a traceback"
                        raise SystemExit(f"{where} block {i}: {what}\n{b['src']}\n---\n{output}")
                    n = len(output.splitlines())
                    if n > DEEP_MAX_LINES:
                        problems.append(f"{where} block {i}: output is {n} lines")
                    b["output"] = output
                b["isError"] = b.pop("raises")
            out.append(b)
        return out

    for t in content.TOPICS:
        if t["id"] in seen:
            raise SystemExit(f"duplicate {name} id: {t['id']}")
        seen.add(t["id"])
        base = t["id"].replace("-", "_")
        sections = []
        for si, s in enumerate(t["sections"]):
            sections.append({
                "title": s["title"],
                "body": render(s["body"], f"{t['id']} / {s['title']}", f"{base}_s{si}"),
            })
        questions = []
        for qi, q in enumerate(t["questions"]):
            if q["level"] not in DEEP_LEVELS:
                problems.append(f"{t['id']} Q{qi + 1}: bad level {q['level']!r}")
            questions.append({
                "q": q["q"],
                "level": q["level"],
                "answer": render(q["answer"], f"{t['id']} / Q{qi + 1}", f"{base}_q{qi}"),
            })
        if "level" in t and t["level"] not in TOPIC_LEVELS:
            problems.append(f"{t['id']}: bad level {t['level']!r}")
        topics.append({
            "id": t["id"],
            "title": t["title"],
            "group": t.get("group"),
            "tags": list(t.get("tags", [])),
            "level": t.get("level"),
            "summary": t.get("summary", ""),
            "intro": t["intro"],
            "sections": sections,
            "questions": questions,
            "refs": [{"label": l, "url": u} for l, u in t.get("refs", [])],
        })

    if problems:
        raise SystemExit(f"{name} validation failed:\n  " + "\n  ".join(problems))

    body = json.dumps(topics, indent=2, ensure_ascii=False)
    out.write_text(
        "/* GENERATED FILE - do not edit by hand.\n"
        f"   Source: content/{package}/   Build: python3 build.py\n"
        "   Every code block below was executed and its output captured. */\n\n"
        f"window.{var} = {body};\n",
        encoding="utf-8")
    print(f"built {len(topics)} {name} topics, {runs} code blocks executed "
          f"-> {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    return len(topics)


def build_deepdive() -> int:
    return build_longform("deepdive", OUT_DEEP, "GRAIL_DEEP", "deep-dive")


def load_generated(path: pathlib.Path, var: str):
    """Read back the JSON payload of a generated data file."""
    text = path.read_text(encoding="utf-8")
    start = text.index(f"window.{var} = ") + len(f"window.{var} = ")
    end = text.index(";\n", start)
    return json.loads(text[start:end])


def build_prep() -> int:
    """Execute every pattern template with its check and emit prep-data.js."""
    import prep

    dsa_ids = {p["id"] for t in load_generated(OUT_DSA, "GRAIL_DSA") for p in t["problems"]}
    patterns, seen = [], set()
    for pat in prep.PATTERNS:
        if pat["id"] in seen:
            raise SystemExit(f"duplicate pattern id: {pat['id']}")
        seen.add(pat["id"])
        out, raised = run_snippet("pattern_" + pat["id"].replace("-", "_"),
                                  pat["template"] + "\n\n" + pat["check"] + "\n")
        if raised:
            raise SystemExit(f"pattern {pat['id']}: template failed its check\n{out}")
        missing = [e for e in pat["examples"] if e not in dsa_ids]
        if missing:
            raise SystemExit(f"pattern {pat['id']}: unknown example problems {missing}")
        patterns.append({k: pat[k] for k in ("id", "name", "signals", "idea", "template", "examples")})

    data = {"patterns": patterns, "complexity": prep.COMPLEXITY, "sizes": prep.INPUT_SIZES}
    OUT_PREP.write_text(
        "/* GENERATED FILE - do not edit by hand.\n"
        "   Source: content/prep.py   Build: python3 build.py\n"
        "   Every pattern template below was executed against its check. */\n\n"
        f"window.GRAIL_PREP = {json.dumps(data, indent=2, ensure_ascii=False)};\n",
        encoding="utf-8")
    print(f"built {len(patterns)} prep patterns, all templates executed -> {OUT_PREP.relative_to(ROOT)}")
    return len(patterns)


def build_databases() -> int:
    return build_longform("databases", OUT_DB, "GRAIL_DB", "databases")


def build_systemdesign() -> int:
    return build_longform("systemdesign", OUT_SD, "GRAIL_SD", "system-design")


def build_lld() -> int:
    return build_longform("lld", OUT_LLD, "GRAIL_LLD", "lld")


def _plain(html: str) -> str:
    """Inline HTML to plain text for the search index."""
    import html as htmllib
    text = htmllib.unescape(re.sub(r"<[^>]+>", "", html))
    return re.sub(r"\s+", " ", text).strip()


def _slug(title: str) -> str:
    """Same as slug() in assets/js/deepdive.js, so section anchors line up."""
    s = re.sub(r"<[^>]+>|&\w+;", "", title).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def build_search() -> int:
    """One compact index over every page of the site, read back from the data
    files the other build steps just wrote. Loaded only by search.html.

    Record: k kind, t title, c context line, u url, b body text to match on,
    d difficulty (optional)."""
    BODY = 240
    recs = []

    def add(kind, title, ctx, url, body="", diff=None):
        r = {"k": kind, "t": _plain(title), "c": _plain(ctx), "u": url,
             "b": _plain(body)[:BODY]}
        if diff:
            r["d"] = diff
        recs.append(r)

    for t in load_generated(OUT_DSA, "GRAIL_DSA"):
        if not t["problems"]:
            continue
        add("dsa-topic", t["title"], f"{len(t['problems'])} problems", f"dsa.html?topic={t['id']}",
            " ".join(sec.get("title", "") for sec in t.get("sections", [])))
        for pr in t["problems"]:
            num = f"{pr['lc']}. " if pr.get("lc") else ""
            add("dsa", num + pr["name"], f"{pr['topicTitle']} / {pr['sectionTitle']}",
                f"problem.html?id={pr['id']}",
                " ".join(pr.get("tags") or []) + " " +
                " ".join(a["name"] for a in pr.get("approaches", [])),
                pr["difficulty"])

    for out, var, page, kind in ((OUT_DEEP, "GRAIL_DEEP", "deepdive.html", "deepdive"),
                                 (OUT_DB, "GRAIL_DB", "databases.html", "databases"),
                                 (OUT_SD, "GRAIL_SD", "systemdesign.html", "systemdesign"),
                                 (OUT_LLD, "GRAIL_LLD", "lld.html", "lld")):
        if not out.exists():
            continue
        for t in load_generated(out, var):
            base = f"{page}?topic={t['id']}"
            add(kind, t["title"], t.get("summary") or "Topic", base,
                " ".join(t.get("tags") or []) + " " + " ".join(t["intro"]), t.get("level"))
            for sec in t["sections"]:
                text = " ".join(b["html"] for b in sec["body"] if b["type"] == "p")
                add(kind, sec["title"], t["title"], f"{base}#{_slug(sec['title'])}", text)
            for q in t["questions"]:
                add(kind, q["q"], f"{t['title']} / interview question",
                    f"{base}#interview-questions", "", q["level"])

    prep = load_generated(OUT_PREP, "GRAIL_PREP")
    for pat in prep["patterns"]:
        add("prep", pat["name"], "Pattern cheat sheet", f"prep.html#p-{pat['id']}",
            pat["idea"] + " " + " ".join(pat["signals"]))
    for grp in prep["complexity"]:
        add("prep", f"{grp['title']} operation costs", "Complexity cheat sheet",
            "prep.html#complexity", " ".join(r[0] for r in grp["rows"]))

    body = json.dumps(recs, ensure_ascii=False, separators=(",", ":"))
    OUT_SEARCH.write_text(
        "/* GENERATED FILE - do not edit by hand. Build: python3 build.py */\n"
        f"window.GRAIL_SEARCH = {body};\n", encoding="utf-8")
    print(f"built search index: {len(recs)} records, {len(body) // 1024} KB "
          f"-> {OUT_SEARCH.relative_to(ROOT)}")
    return len(recs)


def stamp_assets() -> str:
    """Append a content hash to every local stylesheet and script reference, so
    browsers cannot serve a stale style.css or data file after a rebuild."""
    pattern = re.compile(r'((?:href|src)="(assets/(?:css|js)/[\w.-]+\.(?:css|js)))(\?v=[0-9a-f]+)?(")')
    digests = {}

    def stamp(m):
        path = m.group(2)
        if path not in digests:
            digests[path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:8]
        return f"{m.group(1)}?v={digests[path]}{m.group(4)}"

    touched = 0
    for page in sorted(ROOT.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        new = pattern.sub(stamp, text)
        if new != text:
            page.write_text(new, encoding="utf-8")
            touched += 1
    digest = digests.get("assets/css/style.css", "")
    print(f"stamped {len(digests)} asset(s) into {touched} page(s)")
    return digest


def main() -> None:
    sys.path.insert(0, str(ROOT / "content"))

    ver = "%d.%d.%d" % sys.version_info[:3]
    OUT.write_text(
        "/* GENERATED FILE - do not edit by hand. Build: python3 build.py */\n"
        f'window.GRAIL_PYTHON = "{ver}";\n',
        encoding="utf-8",
    )
    print(f"building on CPython {ver}")

    build_dsa()
    build_prep()
    build_deepdive()
    build_databases()
    build_systemdesign()
    build_lld()
    build_search()
    stamp_assets()


if __name__ == "__main__":
    main()
