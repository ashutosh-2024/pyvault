"""Animations for the foundations and 1-D linear DP problems."""
from ._kit import Board, Story, CallTrace, heat_chapter, fmt


def _two_var_chapter(s, title, labels, values, keep, caption_end):
    """Show that only the last `keep` entries are ever read again."""
    ch = s.chapter(title)
    n = len(values)
    for i in range(n):
        b = Board(1, n, row_labels=[labels], col_labels=list(range(n)))
        for j in range(i + 1):
            b.set(0, j, values[j], "dim" if j < i - keep + 1 else "done")
        b.set(0, i, values[i], "cur")
        live = [j for j in range(max(0, i - keep + 1), i + 1)]
        ch.add(b.frame(
            f"Step {i}: only {', '.join(f'<code>{labels}[{j}]</code>' for j in live)} will ever be read again; "
            "everything faded can be forgotten.",
            formula=f"kept in memory: {', '.join(fmt(values[j]) for j in live)}"))
    b = Board(1, n, row_labels=[labels], col_labels=list(range(n)))
    for j in range(n):
        b.set(0, j, values[j], "dim")
    b.set(0, n - 1, values[-1], "answer")
    ch.add(b.frame(caption_end, formula=f"answer = {fmt(values[-1])}"))


# ------------------------------------------------------------------ Fibonacci
def nth_fibonacci():
    N = 6
    s = Story()
    t = CallTrace()

    def f(n):
        with t.call(n):
            return n if n < 2 else f(n - 1) + f(n - 2)

    assert f(N) == 8
    heat_chapter(
        s, "Plain recursion repeats work", t,
        lambda: Board(1, N + 1, row_labels=["calls"], col_labels=list(range(N + 1))),
        lambda k: (0, k),
        f"<code>fib(n) = fib(n-1) + fib(n-2)</code>, written as plain recursion. Watch how many times each "
        f"<code>fib(k)</code> gets computed while evaluating <code>fib({N})</code>.",
        lambda k, n: f"Call <code>fib({k})</code>" + (" &mdash; base case." if k < 2 else ".")
                     + f" Computed {n} time{'s' * (n > 1)} so far.",
        lambda calls, counts: f"<strong>{calls} calls</strong> for {len(counts)} different values. "
                              f"<code>fib(1)</code> alone was computed {counts[1]} times; the count roughly doubles with every +1 to n.")

    ch = s.chapter("Bottom-up table")
    dp = [None] * (N + 1)
    b = Board(1, N + 1, row_labels=["fib"], col_labels=list(range(N + 1)))
    dp[0], dp[1] = 0, 1
    b.set(0, 0, 0, "base").set(0, 1, 1, "base")
    ch.add(b.frame("Start from the two base cases, <code>fib(0) = 0</code> and <code>fib(1) = 1</code>, and build upwards.",
                   formula="fib[0] = 0,  fib[1] = 1"))
    for i in range(2, N + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
        b.set(0, i, dp[i], "done")
        ch.add(b.frame(f"<code>fib[{i}]</code> reads the two entries just before it, both already computed.",
                       formula=f"fib[{i}] = fib[{i-1}] + fib[{i-2}] = {dp[i-1]} + {dp[i-2]} = {dp[i]}",
                       marks={(0, i): "cur", (0, i - 1): "src", (0, i - 2): "src"},
                       arrows=[(0, i - 1, 0, i), (0, i - 2, 0, i)]))
    ch.add(b.frame(f"Each value computed once: <strong>{N - 1} additions</strong> instead of {len(t.events)} calls.",
                   formula=f"fib({N}) = {dp[N]}", marks={(0, N): "answer"}))

    _two_var_chapter(s, "Keep two numbers", "fib", dp, 2,
                     f"Two variables, <code>a, b = b, a + b</code>, give the same <strong>{dp[N]}</strong> in O(1) space.")
    return s.build()


# ------------------------------------------------------------------ Climbing stairs
def climbing_stairs():
    N = 5
    s = Story()
    ch = s.chapter("The question")
    b = Board(1, N + 1, row_labels=["step"], col_labels=list(range(N + 1)), cls="")
    b.set(0, 0, "S", "start").set(0, N, "top", "goal")
    ch.add(b.frame(f"You climb a staircase of {N} steps, taking 1 or 2 steps at a time. "
                   "In how many distinct ways can you reach the top?"))
    for route in ([1, 1, 2, 1], [2, 2, 1]):
        pos, path = 0, [(0, 0)]
        for st in route:
            pos += st
            path.append((0, pos))
        marks = {(0, p): "path" for _, p in path[1:-1]}
        ch.add(b.frame(f"One way: steps of {' + '.join(map(str, route))}.", marks=marks))
    ch.add(b.frame("Key observation: the <strong>last</strong> move onto step i came from step i&minus;1 (a 1-step) "
                   "or step i&minus;2 (a 2-step). Those two groups never overlap, so add them.",
                   formula="ways[i] = ways[i-1] + ways[i-2]"))

    t = CallTrace()

    def f(i):
        with t.call(i):
            return 1 if i <= 1 else f(i - 1) + f(i - 2)

    total = f(N)
    heat_chapter(
        s, "Plain recursion repeats work", t,
        lambda: Board(1, N + 1, row_labels=["calls"], col_labels=list(range(N + 1))),
        lambda k: (0, k),
        f"Recursing on that observation directly: <code>ways({N}) = ways({N-1}) + ways({N-2})</code>, and so on down.",
        lambda k, n: f"Call <code>ways({k})</code>" + (" &mdash; base case (1 way)." if k <= 1 else ".")
                     + f" Computed {n}&times; so far.",
        lambda calls, counts: f"{calls} calls for {len(counts)} distinct steps. The same small sub-answers are "
                              "recomputed again and again.")

    ch = s.chapter("Bottom-up table")
    ways = [1, 1] + [None] * (N - 1)
    b = Board(1, N + 1, row_labels=["ways"], col_labels=list(range(N + 1)))
    b.set(0, 0, 1, "base").set(0, 1, 1, "base")
    ch.add(b.frame("One way to stand on step 0 (do nothing) and one way to reach step 1.",
                   formula="ways[0] = 1,  ways[1] = 1"))
    for i in range(2, N + 1):
        ways[i] = ways[i - 1] + ways[i - 2]
        b.set(0, i, ways[i], "done")
        ch.add(b.frame(f"Arrive at step {i} with a 1-step from {i-1} or a 2-step from {i-2}.",
                       formula=f"ways[{i}] = ways[{i-1}] + ways[{i-2}] = {ways[i-1]} + {ways[i-2]} = {ways[i]}",
                       marks={(0, i): "cur", (0, i - 1): "src", (0, i - 2): "src"},
                       arrows=[(0, i - 1, 0, i), (0, i - 2, 0, i)]))
    assert ways[N] == total
    ch.add(b.frame(f"<strong>{ways[N]} ways</strong> to climb {N} steps &mdash; the Fibonacci sequence in disguise.",
                   formula=f"answer = ways[{N}] = {ways[N]}", marks={(0, N): "answer"}))
    _two_var_chapter(s, "Keep two numbers", "ways", ways, 2,
                     "Only the previous two counts are needed, so two variables replace the table.")
    return s.build()


# ------------------------------------------------------------------ House robber (shared)
def _robber_fill(ch, nums, label="", noun="House"):
    n = len(nums)
    b = Board(2, n, row_labels=["house", "best"], col_labels=list(range(n)))
    b.row(0, nums, "")
    best = [None] * n
    for i in range(n):
        skip = best[i - 1] if i >= 1 else 0
        take = nums[i] + (best[i - 2] if i >= 2 else 0)
        best[i] = max(skip, take)
        b.set(1, i, best[i], "done")
        arrows = [(0, i, 1, i)]
        marks = {(1, i): "cur", (0, i): "src"}
        if i >= 1:
            arrows.append((1, i - 1, 1, i)); marks[(1, i - 1)] = "src"
        if i >= 2:
            arrows.append((1, i - 2, 1, i)); marks[(1, i - 2)] = "src"
        choice = ("either choice gives the same" if take == skip else
                  "better to <strong>take it</strong>" if take > skip else "better to <strong>skip it</strong>")
        ref = lambda k: f"best[{k}] = {best[k]}" if k >= 0 else "nothing (0)"
        ch.add(b.frame(
            f"{label}{noun} {i} ({nums[i]}): <em>skip</em> it and keep {ref(i - 1)}, or <em>take</em> it and add "
            f"{ref(i - 2)}. {choice[0].upper() + choice[1:]}.",
            formula=f"best[{i}] = max({skip}, {nums[i]} + {take - nums[i]}) = {best[i]}",
            marks=marks, arrows=arrows))
    # reconstruct which houses were robbed
    robbed, i = [], n - 1
    while i >= 0:
        prev2 = best[i - 2] if i >= 2 else 0
        if (i == 0 and nums[0] > 0) or (i > 0 and best[i] != best[i - 1]):
            robbed.append(i); i -= 2
        else:
            i -= 1
    marks = {(0, r): "chosen" for r in robbed}
    which = "houses" if noun == "House" else "values"
    marks[(1, n - 1)] = "answer"
    ch.add(b.frame(f"{label}Best total <strong>{best[-1]}</strong>, by taking {which} {sorted(robbed)} "
                   "(found by walking back through the choices).",
                   formula=f"answer = best[{n-1}] = {best[-1]}", marks=marks))
    return best


def house_robber():
    nums = [5, 6, 5, 1, 2, 4]
    s = Story()
    ch = s.chapter("The question")
    b = Board(1, len(nums), row_labels=["house"], col_labels=list(range(len(nums))), cls="")
    b.row(0, nums)
    ch.add(b.frame("Each house holds some money. Robbing two <strong>adjacent</strong> houses triggers the alarm. "
                   "What is the most you can take?"))
    left, greedy, picks = set(range(len(nums))), 0, []
    while left:                                        # grab the biggest remaining house
        i = max(left, key=lambda k: (nums[k], -k))
        picks.append(i); greedy += nums[i]
        left -= {i - 1, i, i + 1}
    ch.add(b.frame(f"Greedy (always grab the biggest house left) takes {' + '.join(str(nums[i]) for i in picks)} = "
                   f"<strong>{greedy}</strong>. Grabbing the 6 blocked both 5s. We need to weigh every choice.",
                   marks={(0, i): "path" for i in picks}))

    t2 = CallTrace()

    def g(i):                     # traced version that skips the i < 0 sentinels
        if i < 0:
            return 0
        with t2.call(i):
            return max(g(i - 1), nums[i] + g(i - 2))

    g(len(nums) - 1)
    heat_chapter(
        s, "Plain recursion repeats work", t2,
        lambda: Board(1, len(nums), row_labels=["calls"], col_labels=list(range(len(nums)))),
        lambda k: (0, k),
        "<code>best(i) = max(best(i-1), nums[i] + best(i-2))</code> as plain recursion. Count the calls per house.",
        lambda k, n: f"Call <code>best({k})</code>; computed {n}&times; so far.",
        lambda calls, counts: f"{calls} calls for {len(counts)} houses &mdash; exponential growth again.")

    ch = s.chapter("Fill the table")
    best = _robber_fill(ch, nums)

    ch = s.chapter("Two variables")
    b = Board(2, len(nums), row_labels=["house", "best"], col_labels=list(range(len(nums))))
    b.row(0, nums, "")
    for i, x in enumerate(best):
        b.set(1, i, x, "dim")
        marks = {(1, i): "cur"}
        if i >= 1: marks[(1, i - 1)] = "src"
        if i >= 2: marks[(1, i - 2)] = "src"
        ch.add(b.frame(f"At house {i} only the previous two bests are read. Keep them as <code>prev2, prev1</code>.",
                       formula=f"prev2, prev1 = prev1, max(prev1, {nums[i]} + prev2)   ->   prev1 = {x}", marks=marks))
    ch.add(b.frame(f"Same answer, <strong>{best[-1]}</strong>, in O(1) extra space.", marks={(1, len(nums) - 1): "answer"}))
    return s.build()


def house_robber_ii():
    nums = [2, 3, 2, 5, 1, 4]
    n = len(nums)
    s = Story()
    ch = s.chapter("The question")
    b = Board(1, n, row_labels=["house"], col_labels=list(range(n)), cls="")
    b.row(0, nums)
    ch.add(b.frame("Same as House Robber, but the houses stand in a <strong>circle</strong>: the first and last are neighbours."))
    ch.add(b.frame("So house 0 and house {} can never both be robbed. Split into two straight-line problems: "
                   "skip the last house, or skip the first.".format(n - 1),
                   marks={(0, 0): "goal", (0, n - 1): "goal"}))

    best_a = _robber_fill(s.chapter("Without the last house"), nums[:-1], "")
    best_b = _robber_fill(s.chapter("Without the first house"), nums[1:], "")

    ch = s.chapter("Take the better one")
    b = Board(2, n, row_labels=["no last", "no first"], col_labels=list(range(n)))
    for i, x in enumerate(best_a):
        b.set(0, i, x, "dim")
    for i, x in enumerate(best_b):
        b.set(1, i + 1, x, "dim")
    b.set(0, n - 1, "", "none").set(1, 0, "", "none")
    ans = max(best_a[-1], best_b[-1])
    win = (0, n - 2) if best_a[-1] >= best_b[-1] else (1, n - 1)
    ch.add(b.frame(f"Excluding the last house gives {best_a[-1]}, excluding the first gives {best_b[-1]}. "
                   f"Every valid plan avoids at least one of the two, so the answer is the larger: <strong>{ans}</strong>.",
                   formula=f"answer = max({best_a[-1]}, {best_b[-1]}) = {ans}",
                   marks={(0, n - 2): "src", (1, n - 1): "src", win: "answer"}))
    return s.build()


# ------------------------------------------------------------------ Maximum subarray (Kadane)
def maximum_subarray():
    nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    n = len(nums)
    s = Story()
    ch = s.chapter("Kadane's scan")
    b = Board(3, n, row_labels=["nums", "ending here", "best"], col_labels=list(range(n)))
    b.row(0, nums, "")
    ch.add(b.frame("Find the contiguous subarray with the largest sum. For each index, track the best sum of a subarray "
                   "that <strong>ends exactly here</strong>, and the best seen anywhere so far."))
    cur = best = None
    start = best_l = best_r = 0
    for i, x in enumerate(nums):
        if cur is None or cur + x < x:
            cur, start, why = x, i, f"starting fresh at {x} beats extending ({'nothing' if i == 0 else fmt(cur) + ' + ' + str(x)})"
        else:
            why = f"extending the run ({cur} + {x}) beats starting over at {x}"
            cur = cur + x
        if best is None or cur > best:
            best, best_l, best_r = cur, start, i
        b.set(1, i, cur, "done").set(2, i, best, "done")
        marks = {(1, i): "cur", (0, i): "src", (2, i): "cur"}
        arrows = [(0, i, 1, i)]
        if i:
            marks[(1, i - 1)] = "src"; arrows.append((1, i - 1, 1, i))
        ch.add(b.frame(f"Index {i}: {why}.",
                       formula=f"ending[{i}] = max({x}, ending[{i-1}] + {x}) = {cur};  best = {best}" if i else
                               f"ending[0] = {x};  best = {best}",
                       marks=marks, arrows=arrows))
    marks = {(0, k): "chosen" for k in range(best_l, best_r + 1)}
    marks[(2, n - 1)] = "answer"
    ch.add(b.frame(f"Largest sum <strong>{best}</strong>, from the subarray {nums[best_l:best_r + 1]} "
                   f"(indices {best_l}&ndash;{best_r}). One pass, O(1) space.",
                   formula=f"answer = {best}", marks=marks))
    assert best == max(sum(nums[i:j]) for i in range(n) for j in range(i + 1, n + 1))
    return s.build()


# ------------------------------------------------------------------ Decode ways
def decode_ways():
    word = "11106"
    n = len(word)
    s = Story()
    ch = s.chapter("The question")
    b = Board(1, n, row_labels=["digit"], col_labels=list(range(n)), cls="")
    b.row(0, list(word))
    ch.add(b.frame("Letters are encoded as 1&rarr;A &hellip; 26&rarr;Z. How many ways can the digit string be decoded? "
                   "Every step either takes <strong>one digit</strong> (1&ndash;9) or <strong>two digits</strong> (10&ndash;26)."))
    ch.add(b.frame("A '0' can never stand alone, so <code>06</code> is not a letter and the '1' before the '0' must pair with it.",
                   marks={(0, 3): "goal"}))

    ch = s.chapter("Fill the table")
    dp = [0] * (n + 1)
    dp[0] = 1
    b = Board(2, n + 1, row_labels=["digit", "ways"], col_labels=list(range(n + 1)))
    b.set(0, 0, "", "none")
    for i, ch_ in enumerate(word):
        b.set(0, i + 1, ch_, "")
    b.set(1, 0, 1, "base")
    ch.add(b.frame("<code>ways[i]</code> = number of decodings of the first i digits. The empty prefix has exactly one decoding.",
                   formula="ways[0] = 1"))
    for i in range(1, n + 1):
        one, two = word[i - 1], word[i - 2:i] if i >= 2 else ""
        parts, arrows, marks = [], [], {(1, i): "cur", (0, i): "src"}
        if one != "0":
            dp[i] += dp[i - 1]; parts.append(f"ways[{i-1}] ({one} alone)")
            arrows.append((1, i - 1, 1, i)); marks[(1, i - 1)] = "src"
        if two and 10 <= int(two) <= 26:
            dp[i] += dp[i - 2]; parts.append(f"ways[{i-2}] ({two} as a pair)")
            arrows.append((1, i - 2, 1, i)); marks[(1, i - 2)] = "src"; marks[(0, i - 1)] = "src"
        b.set(1, i, dp[i], "done")
        ch.add(b.frame(f"Digit {i}: " + (" + ".join(parts) if parts else
                                        f"'{one}' cannot stand alone and '{two}' is not 10&ndash;26, so no decodings")
                       + ".", formula=f"ways[{i}] = {dp[i]}", marks=marks, arrows=arrows))
    ch.add(b.frame(f"<strong>{dp[n]}</strong> decoding{'s' * (dp[n] != 1)} of <code>{word}</code>.",
                   formula=f"answer = ways[{n}] = {dp[n]}", marks={(1, n): "answer"}))
    return s.build()


# ------------------------------------------------------------------ Delete and earn
def delete_and_earn():
    nums = [2, 2, 3, 3, 3, 4]
    s = Story()
    ch = s.chapter("Turn it into House Robber")
    top = max(nums)
    pts = [0] * (top + 1)
    for x in nums:
        pts[x] += x
    b = Board(1, len(nums), row_labels=["nums"], col_labels=list(range(len(nums))), cls="")
    b.row(0, nums)
    ch.add(b.frame("Taking a value x earns x points but deletes every x&minus;1 and x+1. "
                   "If you take one 3, you may as well take all the 3s."))
    b = Board(2, top + 1, row_labels=["value", "points"], col_labels=list(range(top + 1)))
    b.row(0, list(range(top + 1)), "")
    for v in range(top + 1):
        b.set(1, v, pts[v], "done")
        ch.add(b.frame(f"Bucket by value: value {v} appears {nums.count(v)}&times;, worth {pts[v]} points in total.",
                       marks={(1, v): "cur"}))
    ch.add(b.frame("Now taking value v forbids v&minus;1 and v+1: exactly House Robber on the <code>points</code> row."))

    ch = s.chapter("Rob the values")
    best = _robber_fill(ch, pts, noun="Value")
    return s.build()


BUILDERS = {
    "nth-fibonacci": nth_fibonacci,
    "climbing-stairs": climbing_stairs,
    "house-robber": house_robber,
    "house-robber-ii": house_robber_ii,
    "maximum-subarray": maximum_subarray,
    "decode-ways": decode_ways,
    "delete-and-earn": delete_and_earn,
}
