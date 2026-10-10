#!/usr/bin/env python3
"""Check one or more content/explain/ modules without running the full build.

    python3 check_explain.py hashing two_pointers

For every problem in the module(s): the write-up uses the full schema (two or
more worked examples; per approach idea + steps + why >= 8 pointers, one dry
run per example, >= 3 FAQ entries, only allowed inline tags), approach names
match content/, and every approach returns `expect` on every worked example.
Safe to run in parallel with other checks: it writes nothing to the repo.
"""
import importlib
import importlib.util
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "content"))
sys.path.insert(0, str(ROOT))

import subprocess                 # noqa: E402
import build                      # noqa: E402  (helpers only; main() is guarded)
import dsa                        # noqa: E402


def main(mods):
    probs = {}
    for t in dsa.TOPICS:
        head = dsa.PRELUDE + "\n\n" + t.get("prelude", "")
        for s in t.get("sections", []):
            for p in s["problems"]:
                probs[p["id"]] = (p, head)
    bad = 0
    for name in mods:
        # load the file on its own: the package __init__ imports every module,
        # and another module being rewritten may not parse at this moment
        spec = importlib.util.spec_from_file_location(f"_explain_{name}", ROOT / "content" / "explain" / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"FAIL {name}: does not load: {type(e).__name__}: {e}"); bad += 1; continue
        n_ap = 0
        committed = subprocess.run(["git", "show", f"HEAD:content/explain/{name}.py"], cwd=ROOT,
                                   capture_output=True, text=True).stdout
        ns = {}
        if committed:
            exec(committed, ns)
        dropped = [pid for pid in ns.get("EXPLAIN", {}) if pid not in mod.EXPLAIN]
        if dropped:
            print(f"FAIL {name}: {len(dropped)} problem(s) still to write: {dropped}"); bad += 1
        for pid, entry in mod.EXPLAIN.items():
            if pid not in probs:
                print(f"FAIL {pid}: no such problem in content/"); bad += 1; continue
            p, head = probs[pid]
            names = [ap["name"] for ap in p["approaches"]]
            missing = [n for n in names if n not in entry.get("approaches", {})]
            unknown = [n for n in entry.get("approaches", {}) if n not in names]
            if missing or unknown:
                print(f"FAIL {pid}: missing {missing} unknown {unknown}"); bad += 1; continue
            examples = entry.get("examples") or []
            if len(examples) < build.MIN_EXAMPLES:
                print(f"FAIL {pid}: needs {build.MIN_EXAMPLES} worked examples under 'examples'"); bad += 1; continue
            check = "".join(
                (e.get("setup", "") + "\n" + f"__ex = ({e['call']})\n"
                 f"assert __ex == ({e['expect']}), 'worked example {k} returned %r, the write-up says ' % (__ex,) + {e['expect']!r}\n")
                for k, e in enumerate(examples, 1))
            for ap in p["approaches"]:
                where = f"{pid} / {ap['name']}"
                try:
                    w = build.check_write_up(where, entry["approaches"][ap["name"]], len(examples))
                except SystemExit as e:
                    print(f"FAIL {e}"); bad += 1; continue
                case = re.sub(r"[^a-z0-9]+", "_", where.lower())[:60]
                try:
                    out, raised = build.run_snippet(case, head + "\n\n" + ap["code"] + "\n\n" + check)
                except Exception as e:
                    out, raised = repr(e), True
                if raised:
                    print(f"FAIL {where}: {out.strip().splitlines()[-1] if out.strip() else 'raised'}"); bad += 1; continue
                n_ap += 1
        print(f"{name}: {len(mod.EXPLAIN)} problems, {n_ap} approaches OK")
    print("ALL OK" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
