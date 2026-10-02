"""Animations for the Heaps and Priority Queues topic. Heaps are drawn as a
tree and as the array that stores it; every swap is a real sift step from
TracedHeap."""
import bisect
import heapq
from collections import Counter, deque
from ._kit import Board, Story, frame, fmt
from ._heapkit import TracedHeap


def _ev(ev, caption=None, formula=None, board=None, marks=None, arrows=None, trees=None, array=True):
    """Turn a TracedHeap event into a frame, optionally with an input grid above."""
    tr = [ev["tree"]] + (trees or [])
    cap = caption if caption is not None else ev["text"]
    arr = ev["array"] if array else None
    if board is not None:
        return board.frame(cap, formula=formula, marks=marks, arrows=arrows, trees=tr, array=arr)
    return frame(cap, formula=formula, trees=tr, array=arr)


def _row(values, label, cls=""):
    b = Board(1, len(values), row_labels=[label], col_labels=list(range(len(values))), cls=cls)
    b.row(0, values)
    return b


# ================================================================== foundations
def heapify():
    nums = [5, 3, 8, 1, 9, 2]
    s = Story()
    ch = s.chapter("Sift down from the last parent")
    h = TracedHeap("min")
    for ev in h.heapify(nums):
        ch.add(_ev(ev, formula="children of i: 2i+1, 2i+2   parent of i: (i-1)//2"))
    ch.add(frame(f"Result: {h.a}. Only parents were sifted (slots {len(nums) // 2 - 1} down to 0); most nodes are near the "
                 "bottom where a sift is short, which is why heapify is O(n), not O(n log n).",
                 formula="sum over levels of (nodes x height) = O(n)",
                 trees=[h.tree({0: "answer"})], array=h.array({0: "answer"})))

    ch = s.chapter("Pop everything: heapsort")
    out = []
    for _ in range(len(nums)):
        evs = h.pop(detail=False)
        out.append(h.last_popped)
        b = _row(out + [""] * (len(nums) - len(out)), "popped", cls="done")
        for k in range(len(out), len(nums)):
            b.set(0, k, "", "empty")
        ch.add(_ev(evs[0], board=b, marks={(0, len(out) - 1): "chosen"},
                   caption=f"Pop {h.last_popped}, the minimum. The last leaf moves to the root and sifts down."))
        if h.a:
            ch.add(_ev({"tree": h.tree(), "array": h.array(), "text": ""}, board=b,
                       caption=f"Heap repaired: {h.a[0]} is the new minimum.", formula=f"{len(h)} left, each pop O(log n)"))
    return s.build()


# ================================================================== top-k
def kth_largest_element():
    nums, k = [3, 2, 1, 5, 6, 4], 2
    s = Story()
    ch = s.chapter("Min-heap of size k")
    h = TracedHeap("min", label=f"min-heap (k = {k})")
    ch.add(_row(nums, "nums").frame(f"Keep a <strong>min-heap of the k = {k} largest values seen so far</strong>. Its top is the "
                                     "smallest of them, i.e. the k-th largest, and the first thing to evict when something bigger arrives."))
    for i, x in enumerate(nums):
        b = _row(nums, "nums")
        for j in range(i):
            b.set(0, j, nums[j], "dim")
        for ev in h.push(x, detail=False):
            pass
        ch.add(_ev({"tree": h.tree({h.a.index(x): "cur"}), "array": h.array(), "text": ""}, board=b, marks={(0, i): "cur"},
                   caption=f"Push {x}." + (" The heap now has more than k items." if len(h) > k else "")))
        if len(h) > k:
            evs = h.pop()
            for ev in evs:
                ch.add(_ev(ev, board=b, marks={(0, i): "cur"},
                           caption="Evict the smallest: " + ev["text"] if ev is evs[0] else ev["text"]))
    ch.add(_ev({"tree": h.tree({0: "answer"}), "array": h.array({0: "answer"}), "text": ""}, board=_row(nums, "nums", "dim"),
               caption=f"After all {len(nums)} values the heap holds the {k} largest, {sorted(h.a)}; its top, "
                       f"<strong>{h.top()}</strong>, is the k-th largest. O(n log k) time, O(k) space.",
               formula=f"answer = heap[0] = {h.top()}"))
    assert h.top() == sorted(nums)[-k]
    return s.build()


def kth_largest_in_stream():
    k, init, adds = 3, [4, 5, 8, 2], [3, 5, 10, 9, 4]
    s = Story()
    ch = s.chapter("Min-heap capped at k")
    h = TracedHeap("min", label=f"min-heap (k = {k})")
    for x in init:
        h.push(x, detail=False)
        if len(h) > k:
            h.pop(detail=False)
    ch.add(frame(f"Constructor: keep only the {k} largest of {init}. The top is the current {k}rd largest.",
                 formula=f"heap = {sorted(h.a)}", trees=[h.tree({0: "answer"})], array=h.array()))
    for x in adds:
        if len(h) < k or x > h.top():
            evs = h.push(x) if len(h) < k else h.replace_top(x)
            for ev in evs:
                ch.add(_ev(ev, caption=f"add({x}): " + ev["text"]))
        else:
            ch.add(frame(f"add({x}): {x} is not bigger than the top ({h.top()}), so it can never be among the {k} largest. "
                         "Ignore it.", trees=[h.tree({0: "src"})], array=h.array()))
        ch.add(frame(f"add({x}) returns the top: <strong>{h.top()}</strong>.", formula=f"return {h.top()}",
                     trees=[h.tree({0: "answer"})], array=h.array({0: "answer"})))
    return s.build()


def top_k_frequent():
    nums, k = [1, 1, 1, 2, 2, 3, 4, 4, 4, 4], 2
    s = Story()
    cnt = Counter(nums)
    ch = s.chapter("Count, then a heap of size k")
    vals = sorted(cnt)
    b = Board(2, len(vals), row_labels=["value", "count"], col_labels=list(range(len(vals))))
    b.row(0, vals, "")
    for i, v in enumerate(vals):
        b.set(1, i, cnt[v], "done")
    ch.add(b.frame("Count each value first. Now we need the k values with the largest counts."))
    h = TracedHeap("min", label=f"min-heap by count (k = {k})", key=lambda p: p[0], show=lambda p: f"{p[1]}×{p[0]}")
    for i, v in enumerate(vals):
        h.push((cnt[v], v), detail=False)
        msg = f"Push value {v} (count {cnt[v]})."
        if len(h) > k:
            h.pop(detail=False)
            msg += f" More than {k} entries: evict the least frequent, {h.last_popped[1]} (count {h.last_popped[0]})."
        ch.add(b.frame(msg, marks={(0, i): "cur", (1, i): "cur"}, trees=[h.tree()], array=h.array(label="heap")))
    top = sorted((v for c, v in h.a), key=lambda v: -cnt[v])
    ch.add(b.frame(f"The heap holds the answer: <strong>{top}</strong>. Nodes read value&times;count. O(n log k).",
                   trees=[h.tree({i: "answer" for i in range(len(h))})], array=h.array(label="heap")))

    ch = s.chapter("Best: bucket by frequency")
    n = len(nums)
    buckets = [[] for _ in range(n + 1)]
    for v, c in cnt.items():
        buckets[c].append(v)
    b = Board(1, n + 1, row_labels=["values"], col_labels=list(range(n + 1)))
    for c in range(n + 1):
        b.set(0, c, ",".join(map(str, buckets[c])) if buckets[c] else "", "done" if buckets[c] else "empty")
    ch.add(b.frame(f"A count can only be 1..n, so put each value in bucket[count] (column = count). No comparisons needed.",
                   formula="bucket[count].append(value)"))
    got = []
    for c in range(n, 0, -1):
        if not buckets[c]:
            continue
        got += buckets[c]
        ch.add(b.frame(f"Scan buckets from the highest count down. Bucket {c} gives {buckets[c]}.",
                       formula=f"collected = {got[:k]}", marks={(0, c): "chosen" if len(got) <= k else "cur"}))
        if len(got) >= k:
            break
    ch.add(b.frame(f"Stop once {k} values are collected: <strong>{got[:k]}</strong>. O(n) time, no heap at all.",
                   formula=f"answer = {got[:k]}"))
    return s.build()


def sort_by_frequency():
    word = "banana"
    s = Story()
    cnt = Counter(word)
    ch = s.chapter("Max-heap of counts")
    h = TracedHeap("max", label="max-heap by count", key=lambda p: (p[0], p[1]), show=lambda p: f"{p[1]}×{p[0]}")
    for c in sorted(cnt):
        h.push((cnt[c], c), detail=False)
    ch.add(frame(f"Count the letters of <code>{word}</code>, then put (count, letter) pairs into a max-heap.",
                 trees=[h.tree({0: "cur"})], array=h.array(label="heap")))
    out = ""
    while h.a:
        h.pop(detail=False)
        cnum, letter = h.last_popped
        out += letter * cnum
        b = _row(list(out) + [""] * (len(word) - len(out)), "output", cls="done")
        for j in range(len(out), len(word)):
            b.set(0, j, "", "empty")
        ch.add(b.frame(f"Pop the most frequent letter, '{letter}' ({cnum}&times;), and write it {cnum} times.",
                       marks={(0, j): "chosen" for j in range(len(out) - cnum, len(out))},
                       trees=[h.tree()] if h.a else [h.tree()], array=h.array(label="heap")))
    ch.add(_row(list(out), "output", "done").frame(
        f"Result: <strong>{out}</strong>. <code>Counter(s).most_common()</code> does the same sort in one call, which is the "
        "simplest answer; the heap version is what it does underneath.", formula=f'"{out}"'))
    return s.build()


# ================================================================== k-way merge
def sort_nearly_sorted():
    nums, k = [6, 5, 3, 2, 8, 10, 9], 3
    s = Story()
    ch = s.chapter("Sliding min-heap of size k + 1")
    b = _row(nums, "nums")
    ch.add(b.frame(f"Every element is at most k = {k} places from its sorted position, so the smallest remaining element is "
                   f"always among the next k + 1 = {k + 1}. Keep exactly those in a min-heap."))
    h = TracedHeap("min")
    out = []
    for i, x in enumerate(nums):
        h.push(x, detail=False)
        b = _row(nums, "nums")
        for j in range(i):
            b.set(0, j, nums[j], "dim")
        if len(h) > k:
            h.pop(detail=False)
            out.append(h.last_popped)
            msg = f"Push {x}. The heap has {k + 1} items, so its minimum, {h.last_popped}, must be next in sorted order: output it."
        else:
            msg = f"Push {x}. Still filling the first window of {k + 1}."
        ob = Board(2, len(nums), row_labels=["nums", "sorted"], col_labels=list(range(len(nums))))
        ob.row(0, nums, "")
        for j in range(i):
            ob.set(0, j, nums[j], "dim")
        for j in range(len(nums)):
            ob.set(1, j, out[j] if j < len(out) else "", "done" if j < len(out) else "empty")
        marks = {(0, i): "cur"}
        if out and len(h) >= k:
            marks[(1, len(out) - 1)] = "chosen"
        ch.add(ob.frame(msg, marks=marks, trees=[h.tree()], array=h.array()))
    while h.a:
        h.pop(detail=False)
        out.append(h.last_popped)
        ob = Board(2, len(nums), row_labels=["nums", "sorted"], col_labels=list(range(len(nums))))
        ob.row(0, nums, "dim")
        for j in range(len(nums)):
            ob.set(1, j, out[j] if j < len(out) else "", "done" if j < len(out) else "empty")
        ch.add(ob.frame(f"Input exhausted: drain the heap, {h.last_popped} next.", marks={(1, len(out) - 1): "chosen"},
                        trees=[h.tree()], array=h.array()))
    assert out == sorted(nums)
    ch.add(ob.frame(f"Sorted in O(n log k) with an O(k) heap, instead of O(n log n).", formula=f"{out}"))
    return s.build()


def _kway(s, lists, names, title, intro, outro):
    ch = s.chapter(title)
    width = max(map(len, lists))
    b0 = Board(len(lists), width, row_labels=names, col_labels=list(range(width)))
    for r, lst in enumerate(lists):
        for c in range(width):
            b0.set(r, c, lst[c] if c < len(lst) else "", "" if c < len(lst) else "none")
    h = TracedHeap("min", label="min-heap of heads", key=lambda e: (e[0], e[1]), show=lambda e: f"{e[0]}{names[e[1]][0]}")
    for r, lst in enumerate(lists):
        h.push((lst[0], r, 0), detail=False)
    total = sum(map(len, lists))
    out = []

    def board(cur=None):
        b = Board(len(lists), width, row_labels=names, col_labels=list(range(width)))
        for r, lst in enumerate(lists):
            for c in range(width):
                if c >= len(lst):
                    b.set(r, c, "", "none")
                else:
                    taken = any(e[1] == r and e[2] == c for e in out)
                    inheap = any(e[1] == r and e[2] == c for e in h.a)
                    b.set(r, c, lst[c], "dim" if taken else "src" if inheap else "")
        return b

    ch.add(board().frame(intro, trees=[h.tree()],
                         array={"label": "merged", "v": [], "cls": []} if False else None))
    while h.a:
        h.pop(detail=False)
        v, r, c = h.last_popped
        out.append(h.last_popped)
        msg = f"Pop the smallest head, {v} from {names[r]}, and append it."
        if c + 1 < len(lists[r]):
            h.push((lists[r][c + 1], r, c + 1), detail=False)
            msg += f" Push the next element of {names[r]}, {lists[r][c + 1]}."
        else:
            msg += f" {names[r]} is exhausted."
        b = board()
        ch.add(b.frame(msg, marks={(r, c): "chosen"},
                       trees=[h.tree()],
                       array={"label": "merged", "v": [str(e[0]) for e in out], "cls": ["done"] * (len(out) - 1) + ["chosen"]}))
    assert [e[0] for e in out] == sorted(x for lst in lists for x in lst)
    ch.add(board().frame(outro(total, len(lists)), trees=[h.tree()],
                         array={"label": "merged", "v": [str(e[0]) for e in out], "cls": ["answer"] * len(out)}))


def merge_k_sorted_arrays():
    s = Story()
    _kway(s, [[1, 4, 5], [1, 3, 4], [2, 6]], ["A", "B", "C"], "Min-heap of cursors",
          "Each array is sorted, so the overall minimum is always one of the k current <strong>heads</strong>. Keep the heads in a "
          "min-heap (labels show value and array, e.g. <code>1A</code>; highlighted cells are in the heap).",
          lambda n, k: f"All {n} values merged with a heap that never holds more than k = {k} entries: O(n log k).")
    return s.build()


def merge_k_sorted_lists():
    s = Story()
    _kway(s, [[1, 4, 5], [1, 3, 4], [2, 6]], ["L0", "L1", "L2"], "Min-heap of list heads",
          "Same idea with linked lists: the heap holds one node per list (its current head). Pop the smallest, link it after the "
          "tail of the result, and push that node's <code>next</code>. Ties are broken by list index, so nodes are never compared.",
          lambda n, k: f"All {n} nodes relinked in sorted order; the heap never held more than k = {k} nodes. O(n log k) time, "
                       "O(k) extra space &mdash; no new nodes are created.")
    return s.build()


def smallest_range_k_lists():
    lists = [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]
    names = ["A", "B", "C"]
    s = Story()
    ch = s.chapter("Heap of one element per list")
    width = max(map(len, lists))
    h = TracedHeap("min", label="min-heap (one per list)", key=lambda e: (e[0], e[1]), show=lambda e: f"{e[0]}{names[e[1]]}")
    for r, lst in enumerate(lists):
        h.push((lst[0], r, 0), detail=False)
    hi = max(lst[0] for lst in lists)
    best = (h.top()[0], hi)

    def board(range_=None):
        b = Board(len(lists), width, row_labels=names, col_labels=list(range(width)))
        for r, lst in enumerate(lists):
            for c in range(width):
                if c >= len(lst):
                    b.set(r, c, "", "none")
                else:
                    inheap = any(e[1] == r and e[2] == c for e in h.a)
                    b.set(r, c, lst[c], "src" if inheap else "")
        return b

    ch.add(board().frame("A range containing one number from every list must cover one current element of each. Take the "
                         "first element of each list: the range is [heap min, current max].",
                         formula=f"range = [{h.top()[0]}, {hi}]  best = [{best[0]}, {best[1]}]", trees=[h.tree({0: "cur"})]))
    while True:
        v, r, c = h.top()
        if c + 1 >= len(lists[r]):
            ch.add(board().frame(f"The minimum, {v}, is the last element of list {names[r]}. Raising the minimum is impossible "
                                 f"without dropping list {names[r]}, so stop.",
                                 formula=f"best = [{best[0]}, {best[1]}]", trees=[h.tree({0: "cur"})]))
            break
        nxt = lists[r][c + 1]
        h.replace_top((nxt, r, c + 1), detail=False)
        hi = max(hi, nxt)
        lo = h.top()[0]
        improved = hi - lo < best[1] - best[0]
        if improved:
            best = (lo, hi)
        ch.add(board().frame(f"Advance the list holding the minimum ({names[r]}: {v} &rarr; {nxt}). New range [{lo}, {hi}]"
                             + (" &mdash; <strong>smaller</strong>, keep it." if improved else "."),
                             formula=f"range = [{lo}, {hi}]  best = [{best[0]}, {best[1]}]", trees=[h.tree({0: "cur"})]))
    ch.add(board().frame(f"Smallest range: <strong>[{best[0]}, {best[1]}]</strong>. Only the list holding the minimum ever moves, "
                         "because moving any other list could only widen the range.", formula=f"answer = [{best[0]}, {best[1]}]",
                         trees=[h.tree()]))
    return s.build()


def kth_smallest_in_sorted_matrix():
    m, k = [[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8
    n = len(m)
    s = Story()
    ch = s.chapter("Heap of row heads")

    def board(popped, inheap):
        b = Board(n, n)
        for r in range(n):
            for c in range(n):
                b.set(r, c, m[r][c], "dim" if (r, c) in popped else "src" if (r, c) in inheap else "")
        return b

    h = TracedHeap("min", label="min-heap", key=lambda e: e, show=lambda e: str(e[0]))
    for r in range(n):
        h.push((m[r][0], r, 0), detail=False)
    popped = []
    ch.add(board(popped, {(e[1], e[2]) for e in h.a}).frame(
        "Rows are sorted, so this is a k-way merge of the rows: start with every row's first element.", trees=[h.tree()]))
    for i in range(k - 1):
        h.pop(detail=False)
        v, r, c = h.last_popped
        popped.append((r, c))
        if c + 1 < n:
            h.push((m[r][c + 1], r, c + 1), detail=False)
        ch.add(board(set(popped), {(e[1], e[2]) for e in h.a}).frame(
            f"Pop #{i + 1}: {v}." + (f" Push its right neighbour {m[r][c + 1]}." if c + 1 < n else ""),
            formula=f"popped {i + 1} of k-1 = {k - 1}", marks={(r, c): "chosen"}, trees=[h.tree()]))
    ans = h.top()[0]
    ch.add(board(set(popped), {(e[1], e[2]) for e in h.a}).frame(
        f"After k &minus; 1 = {k - 1} pops the top is the k-th smallest: <strong>{ans}</strong>. O(k log n).",
        formula=f"answer = {ans}", marks={(h.top()[1], h.top()[2]): "answer"}, trees=[h.tree({0: "answer"})]))

    ch = s.chapter("Best: binary search on the value")
    lo, hi = m[0][0], m[-1][-1]
    while lo < hi:
        mid = (lo + hi) // 2
        cnt, r, c, cells = 0, n - 1, 0, set()
        while r >= 0 and c < n:
            if m[r][c] <= mid:
                cnt += r + 1
                cells |= {(rr, c) for rr in range(r + 1)}
                c += 1
            else:
                r -= 1
        b = Board(n, n)
        for rr in range(n):
            for cc in range(n):
                b.set(rr, cc, m[rr][cc], "yes" if (rr, cc) in cells else "no")
        go = "the answer is &le; mid" if cnt >= k else "the answer is &gt; mid"
        ch.add(b.frame(f"Guess mid = {mid} in [{lo}, {hi}]. Count cells &le; {mid} with a staircase walk from the bottom-left: "
                       f"{cnt}. Since {cnt} {'&ge;' if cnt >= k else '&lt;'} k = {k}, {go}.",
                       formula=f"lo={lo} hi={hi} mid={mid} count={cnt}"))
        if cnt >= k:
            hi = mid
        else:
            lo = mid + 1
    b = Board(n, n)
    for rr in range(n):
        for cc in range(n):
            b.set(rr, cc, m[rr][cc], "answer" if m[rr][cc] == lo else "")
    ch.add(b.frame(f"lo = hi = <strong>{lo}</strong>: the smallest value with at least k cells &le; it. "
                   "O(n log(max &minus; min)) with O(1) space.", formula=f"answer = {lo}"))
    assert lo == ans == sorted(x for row in m for x in row)[k - 1]
    return s.build()


# ================================================================== greedy with heaps
def kth_smallest_matrix_row_sums():
    mat, k = [[1, 3, 11], [2, 4, 6]], 5
    s = Story()
    ch = s.chapter("Merge one row at a time, keeping k")
    sums = [0]
    for ri, row in enumerate(mat):
        b = Board(len(sums), len(row), row_labels=[f"sum {x}" for x in sums], col_labels=[f"+{x}" for x in row])
        cands = []
        for i, sm in enumerate(sums):
            for j, x in enumerate(row):
                b.set(i, j, sm + x, "")
                cands.append((sm + x, i, j))
        keep = heapq.nsmallest(k, cands)
        marks = {(i, j): "chosen" for _, i, j in keep}
        ch.add(b.frame(f"Row {ri} = {row}: every kept sum (rows) plus every element of this row (columns). Only the "
                       f"<strong>k = {k} smallest</strong> can matter later, so keep those and drop the rest.",
                       formula=f"keep = {sorted(x for x, _, _ in keep)}", marks=marks))
        sums = sorted(x for x, _, _ in keep)
    ch.add(_row(sums, "kept sums", "done").frame(
        f"After the last row, the kept sums are the k smallest overall; the k-th is <strong>{sums[k - 1]}</strong>.",
        formula=f"answer = {sums[k - 1]}", marks={(0, k - 1): "answer"}))
    return s.build()


def connect_sticks():
    sticks = [1, 8, 3, 5]
    s = Story()
    ch = s.chapter("Always merge the two shortest")
    h = TracedHeap("min")
    h.heapify(sticks, detail=False)
    total = 0
    ch.add(frame("Joining two sticks costs their combined length, and the new stick may be joined again. Short sticks get "
                 "re-paid in every later join, so join the two shortest first (Huffman coding's idea).",
                 trees=[h.tree()], array=h.array()))
    while len(h) > 1:
        h.pop(detail=False); a = h.last_popped
        ch.add(frame(f"Pop the shortest: {a}.", formula=f"cost so far = {total}", trees=[h.tree()], array=h.array()))
        h.pop(detail=False); b_ = h.last_popped
        total += a + b_
        evs = h.push(a + b_, detail=False)
        ch.add(_ev(evs[-1], caption=f"Pop the next shortest, {b_}; join them for {a + b_} and push the new stick back.",
                   formula=f"cost += {a} + {b_}  ->  {total}"))
    ch.add(frame(f"One stick left. Total cost <strong>{total}</strong>.", formula=f"answer = {total}",
                 trees=[h.tree({0: "answer"})], array=h.array({0: "answer"})))
    return s.build()


def task_scheduler():
    tasks, n = list("AAABBBCD"), 2
    s = Story()
    cnt = Counter(tasks)
    ch = s.chapter("Simulate with a max-heap")
    h = TracedHeap("max", label="ready (max-heap by count)", key=lambda p: (p[0], -ord(p[1])), show=lambda p: f"{p[1]}×{p[0]}")
    for t, c in sorted(cnt.items()):
        h.push((c, t), detail=False)
    cool = deque()
    timeline = []
    mx0 = max(cnt.values())
    est = max(len(tasks), (mx0 - 1) * (n + 1) + sum(1 for c in cnt.values() if c == mx0))   # schedule length
    time = 0

    def row():
        b = Board(1, est, row_labels=["cpu"], col_labels=list(range(est)))
        for i in range(est):
            b.set(0, i, timeline[i] if i < len(timeline) else "", ("no" if i < len(timeline) and timeline[i] == "idle" else "done")
                  if i < len(timeline) else "empty")
        return b

    def cool_tree():
        return {"label": "cooling queue (task@ready)", "v": [f"{t}@{at}" for at, (c, t) in cool], "cls": ["dim"] * len(cool),
                "flat": True}

    ch.add(row().frame(f"Each time unit, run the task with the most remaining copies that is not cooling down. After running, a "
                       f"task waits n = {n} units. Counts: {dict(sorted(cnt.items()))}.",
                       trees=[h.tree(), cool_tree()]))
    while h.a or cool:
        while cool and cool[0][0] <= time:
            _, item = cool.popleft()
            h.push(item, detail=False)
        if h.a:
            h.pop(detail=False)
            c, t = h.last_popped
            timeline.append(t)
            if c > 1:
                cool.append((time + n + 1, (c - 1, t)))
            msg = f"t = {time}: run {t} ({c - 1} left)" + (f"; it cools until t = {time + n + 1}." if c > 1 else ".")
        else:
            timeline.append("idle")
            msg = f"t = {time}: every remaining task is cooling down, so the CPU idles."
        time += 1
        ch.add(row().frame(msg, marks={(0, time - 1): "cur"}, trees=[h.tree(), cool_tree()]))
    ch.add(row().frame(f"Done in <strong>{len(timeline)}</strong> units.", formula=f"answer = {len(timeline)}",
                       trees=[h.tree(), cool_tree()]))

    ch = s.chapter("Best: counting formula")
    mx = max(cnt.values())
    n_max = sum(1 for c in cnt.values() if c == mx)
    frame_len = (mx - 1) * (n + 1) + n_max
    b = Board(mx, n + 1, row_labels=[f"row {i}" for i in range(mx)], col_labels=list(range(n + 1)))
    top = [t for t, c in sorted(cnt.items()) if c == mx]
    others = [t for t, c in sorted(cnt.items()) for _ in range(c) if c < mx]
    for r in range(mx):
        for c in range(n + 1):
            if r == mx - 1 and c >= n_max:
                b.set(r, c, "", "none")
            elif c < n_max:
                b.set(r, c, top[c], "chosen")
            else:
                b.set(r, c, "idle", "no")
    ch.add(b.frame(f"The most frequent task(s) ({', '.join(top)}, {mx}&times;) need {mx - 1} full gaps of n + 1 = {n + 1} slots, "
                   f"plus a last row holding just the {n_max} most-frequent task(s).",
                   formula=f"(max - 1) * (n + 1) + count_of_max = ({mx}-1)*{n + 1}+{n_max} = {frame_len}"))
    idx = 0
    for c in range(n_max, n + 1):
        for r in range(mx - 1):
            if idx < len(others):
                b.set(r, c, others[idx], "done"); idx += 1
    ch.add(b.frame(f"Other tasks fill the idle slots. Answer = max(frame, number of tasks) = max({frame_len}, {len(tasks)}) = "
                   f"<strong>{max(frame_len, len(tasks))}</strong>, in O(n) with no heap.",
                   formula=f"answer = {max(frame_len, len(tasks))}"))
    assert max(frame_len, len(tasks)) == len(timeline)
    return s.build()


def reorganize_string():
    word = "aaabbc"
    s = Story()
    cnt = Counter(word)
    ch = s.chapter("Max-heap, never the same letter twice")
    h = TracedHeap("max", label="max-heap by count", key=lambda p: (p[0], -ord(p[1])), show=lambda p: f"{p[1]}×{p[0]}")
    for c, n_ in sorted(cnt.items()):
        h.push((n_, c), detail=False)
    out, held = [], None

    def row():
        b = Board(1, len(word), row_labels=["output"], col_labels=list(range(len(word))))
        for i in range(len(word)):
            b.set(0, i, out[i] if i < len(out) else "", "done" if i < len(out) else "empty")
        return b

    def held_tree():
        return {"label": "held back", "v": [f"{held[1]}×{held[0]}"] if held else [], "cls": ["dim"] if held else [], "flat": True}

    ch.add(row().frame(f"Rearrange <code>{word}</code> so no two neighbours are equal. Greedy: always place the most frequent "
                       "letter, but hold it back for one step so it cannot be placed twice in a row.",
                       trees=[h.tree(), held_tree()]))
    while h.a:
        h.pop(detail=False)
        n_, c = h.last_popped
        out.append(c)
        msg = f"Place '{c}', the most frequent available letter" + (f" ({n_ - 1} left)." if n_ > 1 else ", its last copy.")
        if held:
            h.push(held, detail=False)
            msg += f" The held-back '{held[1]}' may be used again, so it returns to the heap."
        held = (n_ - 1, c) if n_ > 1 else None
        if held:
            msg += f" Hold '{c}' back for one step."
        ch.add(row().frame(msg,
                           marks={(0, len(out) - 1): "cur"}, trees=[h.tree(), held_tree()]))
    ok = len(out) == len(word)
    ch.add(row().frame(f"Result: <strong>{''.join(out)}</strong>." if ok else "A letter is left over: impossible.",
                       formula=f'"{"".join(out)}"', trees=[h.tree(), held_tree()]))

    ch = s.chapter("Best: fill even slots, then odd")
    order = sorted(cnt, key=lambda c: -cnt[c])
    res = [""] * len(word)
    i = 0
    b = Board(1, len(word), row_labels=["slots"], col_labels=list(range(len(word))))
    ch.add(b.frame(f"If the most frequent letter appears more than (n + 1) / 2 times it is impossible. Otherwise write letters, "
                   "most frequent first, into slots 0, 2, 4, &hellip; and then 1, 3, 5, &hellip;",
                   formula=f"max count {cnt[order[0]]} <= (n + 1) // 2 = {(len(word) + 1) // 2}"))
    for c in order:
        for _ in range(cnt[c]):
            res[i] = c
            b.set(0, i, c, "done")
            ch.add(b.frame(f"Write '{c}' into slot {i}.", marks={(0, i): "cur"}))
            i += 2
            if i >= len(word):
                i = 1
    ch.add(b.frame(f"Result <strong>{''.join(res)}</strong>: equal letters are always two slots apart. O(n), no heap.",
                   formula=f'"{"".join(res)}"'))
    return s.build()


def ipo():
    k, w = 3, 0
    profits, capital = [1, 2, 3, 5], [0, 1, 1, 3]
    s = Story()
    ch = s.chapter("Two heaps: by capital, by profit")
    projects = sorted(zip(capital, profits))
    locked = TracedHeap("min", label="locked (min-heap by capital)", key=lambda p: p, show=lambda p: f"c{p[0]}:p{p[1]}")
    avail = TracedHeap("max", label="affordable (max-heap by profit)", key=lambda p: p[1], show=lambda p: f"c{p[0]}:p{p[1]}")
    for p in projects:
        locked.push(p, detail=False)
    ch.add(frame(f"Start with capital w = {w} and pick up to k = {k} projects. Each project needs capital c and returns profit p. "
                 "Locked projects wait in a min-heap by capital.",
                 formula=f"w = {w}", trees=[locked.tree(), avail.tree()]))
    for step in range(k):
        moved = []
        while locked.a and locked.top()[0] <= w:
            locked.pop(detail=False)
            avail.push(locked.last_popped, detail=False)
            moved.append(locked.last_popped)
        if moved:
            ch.add(frame(f"With w = {w}, unlock every project with capital &le; {w}: " +
                         ", ".join(f"c{c}:p{p}" for c, p in moved) + ".",
                         formula=f"w = {w}", trees=[locked.tree(), avail.tree({0: "cur"})]))
        if not avail.a:
            ch.add(frame("Nothing affordable: stop early.", formula=f"w = {w}", trees=[locked.tree(), avail.tree()]))
            break
        avail.pop(detail=False)
        c, p = avail.last_popped
        w += p
        ch.add(frame(f"Project {step + 1}: take the most profitable affordable one (c{c}:p{p}). Capital grows to {w}.",
                     formula=f"w = {w - p} + {p} = {w}", trees=[locked.tree(), avail.tree()]))
    ch.add(frame(f"Final capital <strong>{w}</strong>. Each project moves between heaps at most once: O(n log n).",
                 formula=f"answer = {w}", trees=[locked.tree(), avail.tree()]))
    return s.build()


# ================================================================== intervals
def _timeline(intervals, upto, marks=None, label_fn=None):
    T = max(e for _, e in intervals)
    step = 5
    cols = list(range(0, T, step))
    b = Board(len(intervals), len(cols), row_labels=label_fn or [f"[{a},{e})" for a, e in intervals],
              col_labels=cols, cls="")
    for r, (a, e) in enumerate(intervals):
        for ci, t in enumerate(cols):
            if a <= t < e:
                b.set(r, ci, "", "dim" if r >= upto else "done")
            else:
                b.set(r, ci, "", "no")
    return b


def meeting_rooms():
    ivs = [[0, 30], [5, 10], [15, 20]]
    s = Story()
    ch = s.chapter("Sort by start, compare neighbours")
    srt = sorted(ivs)
    ch.add(_timeline(srt, len(srt)).frame("Can one person attend every meeting? Draw each meeting on a timeline (one column per "
                                          "5 minutes) after sorting by start time."))
    for i in range(1, len(srt)):
        prev, cur = srt[i - 1], srt[i]
        clash = cur[0] < prev[1]
        b = _timeline(srt, len(srt))
        for ci in range(len(b.c[0])):
            t = ci * 5
            if cur[0] <= t < min(cur[1], prev[1]) and clash:
                b.set(i, ci, "", "goal").set(i - 1, ci, "", "goal")
        ch.add(b.frame(f"Meeting {cur} starts at {cur[0]}; the previous one ends at {prev[1]}. " +
                       ("<strong>Overlap</strong> &mdash; impossible." if clash else "No overlap."),
                       formula=f"{cur[0]} < {prev[1]} ?  {clash}"))
        if clash:
            break
    ch.add(_timeline(srt, len(srt)).frame("Answer: <strong>false</strong>. After sorting, only neighbours need checking. O(n log n), "
                                          "no heap needed for this one &mdash; Meeting Rooms II is where the heap comes in.",
                                          formula="answer = False"))
    return s.build()


def meeting_rooms_ii():
    ivs = [[0, 30], [5, 10], [15, 20], [10, 25], [25, 35]]
    s = Story()
    ch = s.chapter("Min-heap of end times")
    srt = sorted(ivs)
    h = TracedHeap("min", label="rooms in use (end times)")
    ch.add(_timeline(srt, 0).frame("How many rooms are needed? Process meetings by start time and keep a min-heap of the end times "
                                   "of meetings currently holding a room. Its size is the number of rooms in use.",
                                   trees=[h.tree()]))
    best = 0
    for i, (a, e) in enumerate(srt):
        freed = []
        if h.a and h.top() <= a:
            h.pop(detail=False); freed.append(h.last_popped)
        h.push(e, detail=False)
        best = max(best, len(h))
        msg = f"Meeting [{a}, {e}): " + (f"the earliest room frees at {freed[0]} &le; {a}, so reuse it. " if freed else
                                         ("every room is still busy, so open a new one. " if i else "first meeting takes a room. "))
        ch.add(_timeline(srt, i + 1).frame(msg + f"Rooms in use: {len(h)}.", formula=f"rooms needed so far = {best}",
                                           trees=[h.tree({h.a.index(e): "cur"})]))
    ch.add(_timeline(srt, len(srt)).frame(f"At most <strong>{best}</strong> meetings overlapped, so {best} rooms. Popping only when "
                                          "a room is actually free keeps the heap size equal to rooms in use.",
                                          formula=f"answer = {best}", trees=[h.tree()]))
    return s.build()


def refueling_stops():
    target, start = 100, 10
    stations = [[10, 60], [20, 30], [30, 30], [60, 40]]
    s = Story()
    ch = s.chapter("Max-heap of fuel driven past")
    b = Board(2, len(stations), row_labels=["position", "fuel"], col_labels=list(range(len(stations))))
    for i, (p, f) in enumerate(stations):
        b.set(0, i, p, "").set(1, i, f, "")
    h = TracedHeap("max", label="passed stations' fuel (max-heap)")
    ch.add(b.frame(f"Drive to {target} starting with {start} fuel (1 fuel per mile). Idea: drive past stations without stopping, "
                   "but remember their fuel. When the tank would run dry, retroactively stop at the <strong>biggest</strong> one "
                   "passed so far.", formula=f"reach = {start}", trees=[h.tree()]))
    reach, stops, i = start, 0, 0
    while reach < target:
        while i < len(stations) and stations[i][0] <= reach:
            h.push(stations[i][1], detail=False)
            ch.add(b.frame(f"Station at {stations[i][0]} is within reach ({reach}): drive past it, remember its {stations[i][1]} fuel.",
                           formula=f"reach = {reach}, stops = {stops}", marks={(0, i): "src", (1, i): "src"}, trees=[h.tree()]))
            i += 1
        if not h.a:
            ch.add(b.frame("No fuel left to take: the target is unreachable.", formula="answer = -1", trees=[h.tree()]))
            return s.build()
        h.pop(detail=False)
        reach += h.last_popped
        stops += 1
        ch.add(b.frame(f"Can't reach further. Stop (retroactively) at the passed station with the most fuel: +{h.last_popped}.",
                       formula=f"reach = {reach - h.last_popped} + {h.last_popped} = {reach}, stops = {stops}", trees=[h.tree()]))
    ch.add(b.frame(f"Reach {reach} &ge; {target}: <strong>{stops}</strong> stops. Taking the largest fuel first can never need more "
                   "stops than any other choice.", formula=f"answer = {stops}", trees=[h.tree()]))
    return s.build()


# ================================================================== two heaps
def find_median_from_data_stream():
    stream = [5, 15, 1, 3, 8, 7, 9, 10]
    s = Story()
    ch = s.chapter("Max-heap low half, min-heap high half")
    low = TracedHeap("max", label="low half (max-heap)")
    high = TracedHeap("min", label="high half (min-heap)")

    def med():
        return low.top() if len(low) > len(high) else (low.top() + high.top()) / 2

    ch.add(frame("Keep the smaller half in a max-heap and the larger half in a min-heap, with sizes equal or the low half one "
                 "bigger. The median is then at the top(s).", trees=[low.tree(), high.tree()]))
    seen = []
    for x in stream:
        seen.append(x)
        low.push(x, detail=False)
        ch.add(frame(f"addNum({x}): push it into the low half first.", trees=[low.tree({low.a.index(x): "cur"}), high.tree()]))
        low.pop(detail=False); moved = low.last_popped
        high.push(moved, detail=False)
        ch.add(frame(f"Move the low half's maximum ({moved}) to the high half, so every low value &le; every high value.",
                     trees=[low.tree(), high.tree({high.a.index(moved): "cur"})]))
        if len(high) > len(low):
            high.pop(detail=False); back = high.last_popped
            low.push(back, detail=False)
            ch.add(frame(f"The high half is now bigger: move its minimum ({back}) back to keep sizes balanced.",
                         trees=[low.tree({low.a.index(back): "cur"}), high.tree()]))
        m = med()
        assert m == (sorted(seen)[(len(seen) - 1) // 2] + sorted(seen)[len(seen) // 2]) / 2
        tops = {0: "answer"}
        ch.add(frame(f"findMedian() = <strong>{fmt(m)}</strong> after {len(seen)} numbers.",
                     formula=f"median = {'low top' if len(low) > len(high) else '(low top + high top) / 2'} = {fmt(m)}",
                     trees=[low.tree(tops), high.tree(tops if len(low) == len(high) else None)]))
    return s.build()


def sliding_window_median():
    nums, k = [1, 3, -1, -3, 5, 3, 6, 7], 3
    s = Story()
    expect = [sorted(nums[i:i + k])[k // 2] if k % 2 else
              (sorted(nums[i:i + k])[k // 2 - 1] + sorted(nums[i:i + k])[k // 2]) / 2 for i in range(len(nums) - k + 1)]

    ch = s.chapter("Best: sorted window with bisect")
    window = sorted(nums[:k])
    meds = []
    for i in range(len(nums) - k + 1):
        if i:
            window.pop(bisect.bisect_left(window, nums[i - 1]))
            bisect.insort(window, nums[i + k - 1])
        m = window[k // 2] if k % 2 else (window[k // 2 - 1] + window[k // 2]) / 2
        meds.append(m)
        b = Board(2, len(nums), row_labels=["nums", "sorted win"], col_labels=list(range(len(nums))))
        b.row(0, nums, "dim")
        for j in range(i, i + k):
            b.set(0, j, nums[j], "src")
        for j in range(len(nums)):
            b.set(1, j, window[j] if j < k else "", "done" if j < k else "none")
        b.set(1, k // 2, window[k // 2], "answer")
        ch.add(b.frame(("Window " + str(nums[i:i + k]) + ": " if not i else
                        f"Slide: remove {nums[i - 1]} with bisect + pop, insert {nums[i + k - 1]} with insort. ") +
                       f"The middle of the sorted window is the median, {fmt(m)}.",
                       formula=f"medians = {[fmt(x) for x in meds]}"))
    assert meds == expect

    ch = s.chapter("Two heaps with lazy deletion")
    low, high = TracedHeap("max", label="low (max-heap)"), TracedHeap("min", label="high (min-heap)")
    delayed = Counter()
    sizes = {"low": 0, "high": 0}

    def prune(h):
        while h.a and delayed[h.top()]:
            delayed[h.top()] -= 1
            h.pop(detail=False)

    def rebalance():
        if sizes["low"] > sizes["high"] + 1:
            low.pop(detail=False); high.push(low.last_popped, detail=False)
            sizes["low"] -= 1; sizes["high"] += 1
            prune(low)
        elif sizes["low"] < sizes["high"]:
            high.pop(detail=False); low.push(high.last_popped, detail=False)
            sizes["low"] += 1; sizes["high"] -= 1
            prune(high)

    def add(x):
        if not low.a or x <= low.top():
            low.push(x, detail=False); sizes["low"] += 1
        else:
            high.push(x, detail=False); sizes["high"] += 1
        rebalance()

    def remove(x):
        delayed[x] += 1
        if x <= low.top():
            sizes["low"] -= 1
            if x == low.top():
                prune(low)
        else:
            sizes["high"] -= 1
            if high.a and x == high.top():
                prune(high)
        rebalance()

    def stale(h):
        left = dict(delayed)
        marks = {}
        for idx, v in enumerate(h.a):
            if left.get(v):
                marks[idx] = "dim"; left[v] -= 1
        return marks

    for x in nums[:k]:
        add(x)
    meds2 = []
    for i in range(len(nums) - k + 1):
        if i:
            remove(nums[i - 1]); add(nums[i + k - 1])
        m = low.top() if k % 2 else (low.top() + high.top()) / 2
        meds2.append(m)
        b = _row(nums, "nums", "dim")
        for j in range(i, i + k):
            b.set(0, j, nums[j], "src")
        lm = stale(low); lm.setdefault(0, "answer")
        ch.add(b.frame((f"Window {nums[i:i + k]}." if not i else
                        f"Slide: {nums[i - 1]} leaves (only <em>marked</em> for deletion &mdash; faded if still inside a heap), "
                        f"{nums[i + k - 1]} enters.") + f" Median = low top = {fmt(m)}.",
                       formula=f"valid sizes: low {sizes['low']}, high {sizes['high']};  delayed = {dict(+delayed) or '{}'}",
                       trees=[low.tree(lm), high.tree(stale(high))]))
    assert meds2 == expect
    return s.build()


BUILDERS = {
    "heapify": heapify,
    "kth-largest-element": kth_largest_element,
    "kth-largest-in-stream": kth_largest_in_stream,
    "top-k-frequent": top_k_frequent,
    "sort-by-frequency": sort_by_frequency,
    "sort-nearly-sorted": sort_nearly_sorted,
    "merge-k-sorted-arrays": merge_k_sorted_arrays,
    "merge-k-sorted-lists": merge_k_sorted_lists,
    "smallest-range-k-lists": smallest_range_k_lists,
    "kth-smallest-in-sorted-matrix": kth_smallest_in_sorted_matrix,
    "kth-smallest-matrix-row-sums": kth_smallest_matrix_row_sums,
    "connect-sticks": connect_sticks,
    "task-scheduler": task_scheduler,
    "reorganize-string": reorganize_string,
    "ipo": ipo,
    "meeting-rooms": meeting_rooms,
    "meeting-rooms-ii": meeting_rooms_ii,
    "refueling-stops": refueling_stops,
    "find-median-from-data-stream": find_median_from_data_stream,
    "sliding-window-median": sliding_window_median,
}
