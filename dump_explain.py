"""dump_explain.py <explain-module> [problem-id ...]: each problem's tests, the
original (committed) write-up example and every approach's code.

Problems are listed from the committed version of the module, so a module that
is being rewritten still shows every problem it must cover; each is marked
DONE when the working copy already has it in the new schema."""
import importlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "content"))
import dsa  # noqa: E402

name = sys.argv[1]
want = sys.argv[2:]
committed = subprocess.run(["git", "show", f"HEAD:content/explain/{name}.py"], cwd=ROOT,
                           capture_output=True, text=True).stdout
ns = {}
exec(committed, ns)
original = ns["EXPLAIN"]
current = {}
try:
    cur_ns = {}
    exec((ROOT / "content" / "explain" / f"{name}.py").read_text(), cur_ns)
    current = cur_ns["EXPLAIN"]
except Exception as e:  # a half-written file
    print(f"(working copy does not load: {type(e).__name__}: {e})")
probs = {p["id"]: p for t in dsa.TOPICS for s in t.get("sections", []) for p in s["problems"]}
done = [pid for pid in original if "examples" in current.get(pid, {})]
print(f"{name}: {len(original)} problems, {len(done)} already in the new schema: {done}")
for pid, e in original.items():
    if want and pid not in want:
        continue
    p = probs[pid]
    print("=" * 70)
    print(pid, "|", p["name"], "|", p["difficulty"], "| DONE" if pid in done else "")
    print("old example:", e.get("example") or e.get("examples"))
    print("tests:\n" + p["tests"].strip())
    for ap in p["approaches"]:
        print("-" * 50)
        print("APPROACH:", ap["name"], "|", ap["time"], "|", ap["space"], "| small" if ap.get("small") else "")
        print(ap["code"].rstrip())
