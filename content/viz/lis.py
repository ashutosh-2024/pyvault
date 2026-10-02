"""Animations for the longest-increasing-subsequence family."""
import bisect
from ._kit import Board, Story


def _patience(ch, values, label="nums", what="value"):
    """tails[k] = smallest possible tail of an increasing subsequence of length k + 1."""
    n = len(values)
    tails = []
    for i, x in enumerate(values):
        k = bisect.bisect_left(tails, x)
        action = (f"<code>tails</code> is empty, so {x} starts the first subsequence (length 1)." if not tails else
                  f"{x} is bigger than every tail, so it <strong>extends</strong> the longest subsequence (length {k + 1})."
                  if k == len(tails) else
                  f"{x} equals tails[{k}], so nothing changes (the subsequence must be <em>strictly</em> increasing)."
                  if tails[k] == x else
                  f"{x} <strong>replaces</strong> tails[{k}] = {tails[k]}: a length-{k + 1} subsequence can now end in a smaller value, "
                  "which leaves more room to grow later.")
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
        b = Board(2, n, row_labels=[label, "tails"], col_labels=list(range(n)))
        for j, v in enumerate(values):
            b.set(0, j, v, "dim" if j < i else "")
        for j in range(n):
            b.set(1, j, tails[j] if j < len(tails) else "", "done" if j < len(tails) else "empty")
        ch.add(b.frame(f"Read {what} {x}. {action}",
                       formula=f"k = bisect_left(tails, {x}) = {k};  tails = {tails}",
                       marks={(0, i): "cur", (1, k): "cur"}, arrows=[(0, i, 1, k)]))
    return tails


def longest_increasing_subsequence():
    nums = [10, 9, 2, 5, 3, 7, 101, 18]
    n = len(nums)
    s = Story()
    ch = s.chapter("O(n²) table")
    dp = [1] * n
    prev = [-1] * n
    b = Board(2, n, row_labels=["nums", "lis"], col_labels=list(range(n)))
    b.row(0, nums, "")
    ch.add(b.frame("<code>lis[i]</code> = length of the longest strictly increasing subsequence that <strong>ends at index i</strong>. "
                   "Every element alone is a subsequence of length 1."))
    for i in range(n):
        smaller = [j for j in range(i) if nums[j] < nums[i]]
        for j in smaller:
            if dp[j] + 1 > dp[i]:
                dp[i], prev[i] = dp[j] + 1, j
        b.set(1, i, dp[i], "done")
        marks = {(1, i): "cur", (0, i): "src"}
        for j in smaller:
            marks[(1, j)] = "src"
        ch.add(b.frame(f"Index {i} ({nums[i]}): it can extend any earlier subsequence ending in a smaller value "
                       + (f"(indices {smaller}); the longest of those is {dp[i] - 1}." if smaller else "&mdash; there are none."),
                       formula=f"lis[{i}] = 1 + max(lis[j] for nums[j] < {nums[i]}) = {dp[i]}" if smaller else f"lis[{i}] = 1",
                       marks=marks, arrows=[(1, j, 1, i) for j in smaller if prev[i] == j]))
    end = max(range(n), key=lambda i: dp[i])
    seq, k = [], end
    while k != -1:
        seq.append(k); k = prev[k]
    seq.reverse()
    marks = {(0, k): "chosen" for k in seq}
    marks[(1, end)] = "answer"
    ch.add(b.frame(f"The answer is the largest entry, <strong>{dp[end]}</strong>: e.g. {[nums[k] for k in seq]}. "
                   "Each index looks back at every earlier one, so this is O(n&sup2;).",
                   formula=f"answer = max(lis) = {dp[end]}", marks=marks))

    ch = s.chapter("O(n log n): patience sorting")
    tails = _patience(ch, nums)
    b = Board(2, n, row_labels=["nums", "tails"], col_labels=list(range(n)))
    b.row(0, nums, "dim")
    for j in range(n):
        b.set(1, j, tails[j] if j < len(tails) else "", "done" if j < len(tails) else "empty")
    ch.add(b.frame(f"The length of <code>tails</code> is the answer, <strong>{len(tails)}</strong>. Note that tails itself "
                   f"({tails}) need not be a real subsequence &mdash; only its length is meaningful. Each step is one binary search.",
                   formula=f"answer = len(tails) = {len(tails)}", marks={(1, len(tails) - 1): "answer"}))
    assert len(tails) == dp[end]
    return s.build()


def russian_doll_envelopes():
    env = [[5, 4], [6, 4], [6, 7], [2, 3]]
    s = Story()
    ch = s.chapter("Sort, then LIS")
    n = len(env)
    b = Board(1, n, row_labels=["envelope"], col_labels=list(range(n)), cls="")
    b.row(0, [f"{w}x{h}" for w, h in env])
    ch.add(b.frame("An envelope fits inside another if <strong>both</strong> width and height are strictly smaller. "
                   "How many can be nested?"))
    srt = sorted(env, key=lambda e: (e[0], -e[1]))
    b = Board(1, n, row_labels=["sorted"], col_labels=list(range(n)), cls="")
    b.row(0, [f"{w}x{h}" for w, h in srt])
    ch.add(b.frame("Sort by width ascending, and for <strong>equal widths by height descending</strong>. Now any increasing "
                   "sequence of heights automatically has increasing widths, and two envelopes of the same width can never "
                   "both be picked (their heights go down).",
                   formula="sort(key=lambda e: (w, -h))",
                   marks={(0, i): "src" for i, e in enumerate(srt)
                          if sum(1 for f in srt if f[0] == e[0]) > 1}))
    ch = s.chapter("LIS on heights")
    tails = _patience(ch, [h for _, h in srt], label="height", what="height")
    b = Board(2, n, row_labels=["height", "tails"], col_labels=list(range(n)))
    b.row(0, [h for _, h in srt], "dim")
    for j in range(n):
        b.set(1, j, tails[j] if j < len(tails) else "", "done" if j < len(tails) else "empty")
    ch.add(b.frame(f"<strong>{len(tails)}</strong> envelopes nest: 2x3 &rarr; 5x4 &rarr; 6x7. Without the descending tie-break, "
                   "6x4 and 6x7 would wrongly count as nested.",
                   formula=f"answer = {len(tails)}", marks={(1, len(tails) - 1): "answer"}))
    return s.build()


def maximum_length_of_pair_chain():
    pairs = [[1, 2], [7, 8], [4, 5], [2, 3], [5, 6], [3, 9]]
    s = Story()
    ch = s.chapter("Greedy by earliest end")
    n = len(pairs)
    b = Board(1, n, row_labels=["pair"], col_labels=list(range(n)), cls="")
    b.row(0, [f"{a},{b2}" for a, b2 in pairs])
    ch.add(b.frame("A pair (c, d) can follow (a, b) if b &lt; c. Find the longest chain. Like activity selection: "
                   "always take the pair that <strong>ends earliest</strong>, leaving the most room for the rest."))
    srt = sorted(pairs, key=lambda p: p[1])
    b = Board(1, n, row_labels=["by end"], col_labels=list(range(n)), cls="")
    b.row(0, [f"{a},{b2}" for a, b2 in srt])
    ch.add(b.frame("Sort by the second number."))
    end, count, chosen = float("-inf"), 0, []
    for i, (a, b2) in enumerate(srt):
        if a > end:
            end, count = b2, count + 1
            chosen.append(i)
            msg = f"({a}, {b2}) starts after {('the last end' if count > 1 else 'nothing')}: take it. Chain length {count}."
        else:
            msg = f"({a}, {b2}) starts at {a}, not after the current end {end}: skip it."
        marks = {(0, j): "chosen" for j in chosen}
        marks[(0, i)] = "cur" if i in chosen else "no"
        b2_ = Board(1, n, row_labels=["by end"], col_labels=list(range(n)), cls="")
        b2_.row(0, [f"{x},{y}" for x, y in srt])
        ch.add(b2_.frame(msg, formula=f"last end = {end};  length = {count}", marks=marks))
    ch.add(b2_.frame(f"Longest chain: <strong>{count}</strong> pairs. The O(n&sup2;) LIS-style DP gives the same answer; greedy is O(n log n).",
                     formula=f"answer = {count}", marks={(0, j): "chosen" for j in chosen}))
    return s.build()


BUILDERS = {
    "longest-increasing-subsequence": longest_increasing_subsequence,
    "russian-doll-envelopes": russian_doll_envelopes,
    "maximum-length-of-pair-chain": maximum_length_of_pair_chain,
}
