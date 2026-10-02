"""Animations for interval DP: tables over [i, j] filled shortest interval first."""
from math import inf
from ._kit import Board, Story


def _upper(n, labels):
    b = Board(n, n, row_labels=labels, col_labels=labels)
    for i in range(n):
        for j in range(i):
            b.set(i, j, "", "none")
    return b


# ------------------------------------------------------------------ palindromes
def _pal_table(s, w, longest):
    n = len(w)
    ch = s.chapter("Fill by length")
    labels = [f"{i}:{c}" for i, c in enumerate(w)]
    pal = [[False] * n for _ in range(n)]
    b = _upper(n, labels)
    count, best = 0, (0, 0)
    for i in range(n):
        pal[i][i] = True; b.set(i, i, True, "yes"); count += 1
    ch.add(b.frame(f"<code>pal[i][j]</code> = is <code>{w}[i..j]</code> a palindrome? Every single letter is one."
                   + (f" ({count} so far)" if not longest else ""), formula="pal[i][i] = True"))
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            inner_ok = length == 2 or pal[i + 1][j - 1]
            pal[i][j] = w[i] == w[j] and inner_ok
            b.set(i, j, pal[i][j], "yes" if pal[i][j] else "no")
            if pal[i][j]:
                count += 1
                if length > best[1] - best[0] + 1:
                    best = (i, j)
            marks, arrows = {(i, j): "cur"}, []
            if length > 2:
                marks[(i + 1, j - 1)] = "src"; arrows.append((i + 1, j - 1, i, j))
            reason = ("ends differ" if w[i] != w[j] else
                      "ends match" + ("" if length == 2 else " and the inside is a palindrome" if inner_ok else
                                      " but the inside is not a palindrome"))
            tally = f"  count = {count}" if not longest else f"  longest = {w[best[0]:best[1]+1]}"
            ch.add(b.frame(f"<code>{w[i:j+1]}</code>: {reason}.",
                           formula=(f"pal[{i}][{j}] = ({w[i]} == {w[j]}) and pal[{i+1}][{j-1}] = {pal[i][j]}" if length > 2
                                    else f"pal[{i}][{j}] = ({w[i]} == {w[j]}) = {pal[i][j]}") + ";" + tally,
                           marks=marks, arrows=arrows))
    return ch, b, pal, count, best


def palindromic_substrings():
    w = "aaba"
    s = Story()
    ch, b, pal, count, best = _pal_table(s, w, longest=False)
    ch.add(b.frame(f"<strong>{count}</strong> palindromic substrings: every True cell is one. Expanding around each of the "
                   f"2n &minus; 1 centres finds the same {count} in O(1) extra space.", formula=f"answer = {count}"))

    ch = s.chapter("Expand around centres")
    n = len(w)
    found = 0
    for centre in range(2 * n - 1):
        lo, hi = centre // 2, (centre + 1) // 2
        b = Board(1, n, row_labels=["s"], col_labels=list(range(n)), cls="")
        b.row(0, list(w))
        spans = []
        while lo >= 0 and hi < n and w[lo] == w[hi]:
            spans.append((lo, hi)); found += 1
            lo, hi = lo - 1, hi + 1
        marks = {}
        for lo2, hi2 in spans:
            for k in range(lo2, hi2 + 1):
                marks[(0, k)] = "chosen"
        kind = "letter" if centre % 2 == 0 else "gap"
        ch.add(b.frame(f"Centre on {kind} {centre / 2:g}: expands to " +
                       (", ".join(f"<code>{w[x:y+1]}</code>" for x, y in spans) if spans else "nothing") + ".",
                       formula=f"found so far = {found}", marks=marks))
    assert found == count
    return s.build()


def longest_palindromic_substring():
    w = "cbbdbbe"
    s = Story()
    ch, b, pal, count, best = _pal_table(s, w, longest=True)
    i, j = best
    marks = {(i, j): "answer"}
    ch.add(b.frame(f"The longest True interval is [{i}, {j}]: <strong><code>{w[i:j+1]}</code></strong>, length {j - i + 1}.",
                   formula=f"answer = {w[i:j+1]}", marks=marks))
    return s.build()


# ------------------------------------------------------------------ split-point interval DP (shared)
def _split_dp(ch, n, labels, base_val, cost, describe, unit):
    """dp[i][j] = min over k in (i..j) of dp[i][k] + dp[k][j] + cost(i, k, j), for j - i >= 2."""
    dp = [[0] * n for _ in range(n)]
    b = _upper(n, labels)
    for i in range(n - 1):
        b.set(i, i + 1, base_val, "base")
    for i in range(n):
        b.set(i, i, "", "none")
    ch.add(b.frame(describe, formula=f"dp[i][i+1] = {base_val}"))
    for gap in range(2, n):
        for i in range(n - gap):
            j = i + gap
            cands = {k: dp[i][k] + dp[k][j] + cost(i, k, j) for k in range(i + 1, j)}
            k = min(cands, key=cands.get)
            dp[i][j] = cands[k]
            b.set(i, j, dp[i][j], "done")
            ch.add(b.frame(f"Interval [{i}, {j}]: try each split point k in between and keep the cheapest. Best is k = {k}.",
                           formula="; ".join(f"k={kk}: {dp[i][kk]}+{dp[kk][j]}+{cost(i, kk, j)}={v}" for kk, v in cands.items()),
                           marks={(i, j): "cur", (i, k): "src", (k, j): "src"},
                           arrows=[(i, k, i, j), (k, j, i, j)]))
    return b, dp


def matrix_chain_multiplication():
    dims = [40, 20, 30, 10, 30]          # matrices A(40x20) B(20x30) C(30x10) D(10x30)
    n = len(dims)
    s = Story()
    ch = s.chapter("The question")
    names = "ABCD"
    b = Board(1, n - 1, row_labels=["matrix"], col_labels=list(names), cls="")
    b.row(0, [f"{dims[i]}x{dims[i+1]}" for i in range(n - 1)])
    ch.add(b.frame("Multiplying a p&times;q by a q&times;r matrix costs p&middot;q&middot;r scalar multiplications. "
                   "The product A&middot;B&middot;C&middot;D can be parenthesised in many ways with very different costs. Find the cheapest."))
    ch = s.chapter("Fill by interval length")
    b, dp = _split_dp(
        ch, n, [f"d{i}={d}" for i, d in enumerate(dims)], 0,
        lambda i, k, j: dims[i] * dims[k] * dims[j],
        "Use the dimension boundaries d0..d4 as indices: <code>dp[i][j]</code> = cheapest cost to multiply the matrices between "
        "boundary i and boundary j. A single matrix (j = i + 1) costs nothing.", "mult")
    from functools import cache

    @cache
    def worst(i, j):
        return 0 if j - i < 2 else max(worst(i, k) + worst(k, j) + dims[i] * dims[k] * dims[j] for k in range(i + 1, j))

    ch.add(b.frame(f"Cheapest total <strong>{dp[0][n-1]:,}</strong> multiplications; the worst order would cost "
                   f"{worst(0, n - 1):,} ({worst(0, n - 1) / dp[0][n-1]:.1f}&times; more). Interval DP tries every split of every "
                   "interval exactly once, O(n&sup3;).",
                   formula=f"answer = dp[0][{n-1}] = {dp[0][n-1]}", marks={(0, n - 1): "answer"}))
    return s.build()


def minimum_cost_to_cut_a_stick():
    length, cuts = 7, [1, 3, 4, 5]
    pts = [0] + sorted(cuts) + [length]
    n = len(pts)
    s = Story()
    ch = s.chapter("The question")
    b = Board(1, length + 1, row_labels=["stick"], col_labels=list(range(length + 1)), cls="")
    for x in range(length + 1):
        b.set(0, x, "|" if x in cuts else "", "path" if x in cuts else "")
    ch.add(b.frame(f"A stick of length {length} must be cut at {cuts}. Each cut costs the length of the piece being cut. "
                   "The order matters: cutting the middle first keeps later pieces short."))
    ch = s.chapter("Fill by interval length")
    b, dp = _split_dp(
        ch, n, [f"p={p}" for p in pts], 0,
        lambda i, k, j: pts[j] - pts[i],
        f"Index the cut positions with both ends added: {pts}. <code>dp[i][j]</code> = cheapest way to make every cut strictly "
        "between point i and point j. Neighbouring points have nothing between them.", "len")
    ch.add(b.frame(f"Minimum total cost <strong>{dp[0][n-1]}</strong>. Whichever cut is made <em>first</em> inside an interval costs "
                   "that interval's full length and splits it into two independent halves, so try each cut as the first.",
                   formula=f"answer = dp[0][{n-1}] = {dp[0][n-1]}", marks={(0, n - 1): "answer"}))
    return s.build()


def burst_balloons():
    nums = [3, 1, 5, 8]
    vals = [1] + nums + [1]
    n = len(vals)
    s = Story()
    ch = s.chapter("The question")
    b = Board(1, n, row_labels=["balloon"], col_labels=list(range(n)), cls="")
    b.row(0, vals)
    b.set(0, 0, 1, "dim").set(0, n - 1, 1, "dim")
    ch.add(b.frame("Bursting balloon i earns left &times; i &times; right, using its current neighbours. Maximise the total. "
                   "Pad both ends with an imaginary 1."))
    ch.add(b.frame("Thinking about which balloon to burst <em>first</em> is hard, because neighbours keep changing. Think about "
                   "which balloon k inside an open interval (i, j) bursts <strong>last</strong>: at that moment its neighbours are "
                   "exactly i and j, and the two sides are independent."))
    ch = s.chapter("Fill by interval length")
    dp = [[0] * n for _ in range(n)]
    b = _upper(n, [f"{i}:{v}" for i, v in enumerate(vals)])
    for i in range(n - 1):
        b.set(i, i + 1, 0, "base")
    for i in range(n):
        b.set(i, i, "", "none")
    ch.add(b.frame("<code>dp[i][j]</code> = best coins from bursting every balloon strictly between i and j. With nothing "
                   "between them that is 0.", formula="dp[i][i+1] = 0"))
    for gap in range(2, n):
        for i in range(n - gap):
            j = i + gap
            cands = {k: dp[i][k] + dp[k][j] + vals[i] * vals[k] * vals[j] for k in range(i + 1, j)}
            k = max(cands, key=cands.get)
            dp[i][j] = cands[k]
            b.set(i, j, dp[i][j], "done")
            ch.add(b.frame(f"Open interval ({i}, {j}): balloon {k} (value {vals[k]}) burst last earns "
                           f"{vals[i]}&times;{vals[k]}&times;{vals[j]} plus the best of each side.",
                           formula="; ".join(f"k={kk}: {v}" for kk, v in cands.items()) + f"  ->  {dp[i][j]}",
                           marks={(i, j): "cur", (i, k): "src", (k, j): "src"},
                           arrows=[(i, k, i, j), (k, j, i, j)]))
    ch.add(b.frame(f"Maximum coins: <strong>{dp[0][n-1]}</strong>.", formula=f"answer = dp[0][{n-1}] = {dp[0][n-1]}",
                   marks={(0, n - 1): "answer"}))
    return s.build()


BUILDERS = {
    "palindromic-substrings": palindromic_substrings,
    "longest-palindromic-substring": longest_palindromic_substring,
    "matrix-chain-multiplication": matrix_chain_multiplication,
    "burst-balloons": burst_balloons,
    "minimum-cost-to-cut-a-stick": minimum_cost_to_cut_a_stick,
}
