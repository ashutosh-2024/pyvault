# pyvault

> Interview prep in Python, all of it executed.

DSA problems by pattern, a deep dive into how CPython works, database
internals, system design and low-level design, plus a pattern cheat sheet,
mock interviews and one search box over all of it.

Split out of [python-grail](https://github.com/ashutosh-2024/python-grail),
which now holds only the gotcha entries.

## The one rule

**No output on this site is written by hand.** `build.py` runs every DSA
solution against its tests and executes every code block in the long-form
sections, capturing what actually came back. If any of that stops being true,
the build fails rather than shipping a page that lies.

## Running locally

```bash
python3 -m http.server 8000     # then open http://localhost:8000
python3 build.py                # regenerate assets/js/*-data.js after editing content/
```

## Deploying

Static site. `.nojekyll` stops GitHub Pages running the files through Jekyll.

## The DSA section

Interview problems by topic. Each problem page carries the LeetCode statement,
examples and constraints, then every worthwhile approach with its time and
auxiliary space cost and the reason that bound holds.

Currently **336 problems, 826 solutions** across all 16 topics: Binary Trees (99),
Heaps (20), Dynamic Programming (33), Backtracking (25), and the NeetCode 250
topics — Arrays and Hashing (21), Two Pointers and Intervals (18), Sliding
Window (9), Stacks (14), Binary Search (14), Linked Lists (13), Tries (3), Union
Find (5), Bit Manipulation (10), Greedy (13), Math and Geometry (13), Graphs (26).
None are placeholders any more.

Dynamic Programming is organised by **pattern** rather than as one flat list:
`dsa.html?topic=dp` lists the seven patterns, and
`dsa.html?topic=dp&pattern=<id>` shows that pattern's explanation followed by
its problems. A topic opts into this with `layout="patterns"`; each section
then supplies `summary` (one line, shown on its box) and `idea` (paragraphs).

### Where the content comes from

Two sources, kept apart on purpose:

- **Pedagogy** — `content/dsa.py` plus the `content/trees_*.py` and
  `content/bst_*.py` modules (trees), `content/heap.py` (heaps) and
  `content/dp.py` (dynamic programming): the
  approaches, complexity reasoning, code and tests.
- **Problem statements** — `content/leetcode.json`, fetched from LeetCode's
  GraphQL API by `fetch_leetcode.py` and committed, so the site build never
  needs the network.

```bash
python3 fetch_leetcode.py          # fetch anything new
python3 fetch_leetcode.py --force  # refetch everything
python3 build.py                   # run all solutions, regenerate data
```

The build cross-checks the fetched metadata against what the entry claims and
fails on any mismatch: wrong LeetCode number, wrong difficulty, a slug missing
from the cache, or a URL that does not match its slug.

> LeetCode statements, examples and constraints are reproduced from their API.
> That is their content; if you would rather not republish it, replace the
> `statement` field per problem and the fetch becomes metadata-only.

### Step-by-step animations

Every Dynamic Programming problem has an animation ("Watch the algorithm run"
on the problem page). Generators live in [`content/viz/`](content/viz/), one
function per problem, registered in `content/viz/__init__.py`. They build
frames by **running** the algorithm (with `_kit.py`'s `Board`, `Story` and
`CallTrace` helpers) - no numbers are typed by hand - and `build.py` validates
each animation, writes it to `assets/viz/<id>.json` (fetched only when a reader
opens the section) and fails if any problem in a topic listed in
`REQUIRED_TOPICS` lacks one. The player is `assets/js/viz.js`.

### Adding a problem

Append to the relevant topic's `sections[...]["problems"]`:

| field | notes |
| --- | --- |
| `id` | kebab-case, becomes `problem.html?id=` |
| `lc` / `slug` | LeetCode number and URL slug. Omit both for a non-LeetCode entry |
| `name`, `difficulty` | difficulty must match LeetCode's or the build fails |
| `approaches` | `name`, `time`, `space`, `why`, `code`, `best`, `tag` |
| `tests` | assertions run against **every** approach |
| `pitfall` | optional; the mistake people actually make |
| `ref` | optional `(label, url)` for a non-LeetCode source, e.g. GeeksforGeeks |

`statement`, `examples`, `constraints` and `tags` come from the cache
automatically. Supply them inline only for premium or non-LeetCode problems —
the build refuses a problem with no statement from either source.

Exactly one approach per problem should set `best=True`.

A topic may define `prelude` for helpers its solutions share (`ListNode`,
`heapq` imports); it is prepended after the global `PRELUDE`.

## The Python Deep Dive section

[`content/deepdive/`](content/deepdive/) holds fifteen long-form topics on how
CPython works — the GIL, memory management, bytecode, the object model,
magic (dunder) methods, descriptors, metaclasses, MRO, `__slots__`/dataclasses/
typing, decorators, generators and iterators, context managers, the import
system, async internals and asyncio pitfalls. Each topic is theory with runnable examples, then medium/hard
interview questions with answers.

The one rule holds here too: every `code(...)` block is executed by
`build.py` and its captured output is shipped beside it. A block that raises
without `raises=True` (or vice versa) fails the build. Write prose that stays
true to what the build prints — bytecode and GC details change between
versions, so re-read the outputs after upgrading Python.

One module per topic; order is set in `content/deepdive/__init__.py`. The
block helpers and schema are in [`_blocks.py`](content/deepdive/_blocks.py):

| block | notes |
| --- | --- |
| `"text"` | a paragraph; inline `<code>`, `<strong>`, `<em>`, `<br>` allowed |
| `code(src, label=, raises=)` | **executed**; output rendered below it |
| `table(head, rows)` | comparison grid |
| `note(text)` | rule-of-thumb callout |
| `caveat(text)` | CPython implementation detail, not a guarantee |

## The Databases section

[`content/databases/`](content/databases/) holds fourteen topics on how
databases work: B+ tree indexes, transactions and MVCC, locking, query
execution, storage internals, Redis, replication, sharding, WAL and
durability, backups and recovery, normalization, SQL, columnar storage and
caching. Topics use the same blocks as the Deep Dive (import them from
`deepdive._blocks`) and add a one-line `summary` for the topic card.
`deepdive.js` renders both sections; `databases.html` points it at
`window.GRAIL_DB` through `data-*` attributes on `#deepdive`.

Examples run against SQLite from the standard library, so query plans,
isolation behaviour and WAL sizes are what that engine actually did. Where
SQLite cannot show a behaviour (Redis structures, replication, sharding) a
small deterministic model stands in. To measure work without timings, some
snippets count SQLite VM instructions with the progress handler.

## The System Design section

[`content/systemdesign/`](content/systemdesign/) holds ten topics: the
interview framework and estimation, load balancing, API design, rate limiting,
unique IDs, queues and delivery guarantees, timeouts/retries/circuit breakers,
and three walkthroughs (URL shortener, news feed, chat). Same blocks and
`summary` field as Databases, same renderer (`systemdesign.html` points
`deepdive.js` at `window.GRAIL_SD`). Every code block is a small, seeded Python
simulation of the mechanism under discussion — a rate limiter, a balancer, a
retry storm — executed by the build like everything else. Caching, sharding
and replication live in Databases and are not repeated here.

## The Low-Level Design section

[`content/lld/`](content/lld/) holds six pattern guides (how to approach an LLD
round and choose a pattern, SOLID, creational, structural, and two behavioral
pages) followed by 35 design problems. Every problem is built with `problem()`
from [`_lld.py`](content/lld/_lld.py), so all of them share one shape:
requirements, a "signal in the problem → pattern → why" table, the class
design, a complete implementation with a demo (executed by the build), how the
design absorbs the likely follow-up change, and interview questions.

Topics carry `group`, `tags` (patterns used) and `level`; `deepdive.js` uses
them to group the index, filter problems by pattern and show difficulty. The
"Practise each pattern" table on the approach page is generated from the
problems' tags in `content/lld/__init__.py`.

## Interview prep, search and site chrome

- `prep.html` — pattern cheat sheet (every template in `content/prep.py` is
  executed against its `check`, and its example problem ids are validated),
  the Python complexity sheet, and a timed mock interview drawn from the DSA
  problems.
- `search.html` — one search box over DSA problems, Deep Dive,
  Databases, System Design and Prep. `build.py` writes a compact
  `assets/js/search-index.js` from the other generated data files, so the
  search page never loads the multi-megabyte DSA data. Press `/` on any page.
- Light/dark theme: `assets/js/theme.js` runs in `<head>` (saved choice, else
  the OS preference) and `app.js` adds the toggle to the nav. Colours are CSS
  tokens; the light palette overrides them under `[data-theme="light"]`.
- `app.js` also adds a Copy button to every source code block, including ones
  rendered later, via a `MutationObserver`.

## Layout

```
index.html            home — links into every section
dsa.html              DSA topic index, or one topic via ?topic=
problem.html          single DSA problem via ?id=
deepdive.html         Deep Dive topic boxes, or one topic via ?topic=
databases.html        Databases topics, same renderer as the Deep Dive
systemdesign.html     System Design topics, same renderer
lld.html              Low-Level Design: pattern guides + 35 design problems
prep.html             patterns, complexity sheet, mock interview
search.html           site-wide search over search-index.js
build.py              runs every DSA solution and code block; fails loudly
fetch_leetcode.py     caches problem statements into content/leetcode.json
content/dsa.py        DSA topics (other content/*.py modules hold their sections)
content/deepdive/     Python Deep Dive topics, one module each
content/databases/    Databases topics, one module each
content/systemdesign/ System Design topics, one module each
content/lld/          LLD pattern guides and design problems
content/prep.py       pattern cheat sheet + complexity tables
content/viz/          step-by-step animation generators
content/leetcode.json GENERATED by fetch_leetcode.py
assets/js/app.js      shared helpers + a hand-rolled Python highlighter
assets/js/data.js     GENERATED — interpreter version only
assets/js/*-data.js   GENERATED — do not edit
assets/css/           one stylesheet
```
