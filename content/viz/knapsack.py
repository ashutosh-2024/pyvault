"""Animations for the knapsack-pattern DP problems."""
from math import inf, isqrt
from ._kit import Board, Story, CallTrace, heat_chapter, fmt


# ------------------------------------------------------------------ 0/1 knapsack
def knapsack_01():
    weights, values, W = [1, 3, 4, 5], [1, 4, 5, 7], 7
    n = len(weights)
    labels = ["none"] + [f"w{w} v{v}" for w, v in zip(weights, values)]
    s = Story()
    ch = s.chapter("Fill the table")
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    b = Board(n + 1, W + 1, row_labels=labels, col_labels=list(range(W + 1)))
    b.row(0, dp[0], "base")
    ch.add(b.frame("<code>dp[i][c]</code> = best value using only the first i items with capacity c. "
                   "With no items the value is 0 for every capacity. Columns are capacities.",
                   formula="dp[0][c] = 0"))
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(W + 1):
            skip = dp[i - 1][c]
            take = dp[i - 1][c - w] + v if c >= w else None
            dp[i][c] = max(skip, take) if take is not None else skip
            b.set(i, c, dp[i][c], "done")
            marks, arrows = {(i, c): "cur", (i - 1, c): "src"}, [(i - 1, c, i, c)]
            if take is not None:
                marks[(i - 1, c - w)] = "src"; arrows.append((i - 1, c - w, i, c))
                why = (f"skip = {skip}, take = {v} + dp[{i-1}][{c - w}] = {take}; "
                       + ("take it." if take > skip else "skip it." if take < skip else "tie."))
                formula = f"dp[{i}][{c}] = max({skip}, {v} + {dp[i-1][c-w]}) = {dp[i][c]}"
            else:
                why = f"the item (weight {w}) does not fit in capacity {c}, so copy the value above."
                formula = f"dp[{i}][{c}] = dp[{i-1}][{c}] = {skip}"
            ch.add(b.frame(f"Item {i} (weight {w}, value {v}), capacity {c}: {why}",
                           formula=formula, marks=marks, arrows=arrows))
    # reconstruct
    chosen, c = [], W
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            chosen.append(i); c -= weights[i - 1]
    marks, c = {}, W
    for i in range(n, 0, -1):
        marks[(i, c)] = "chosen" if i in chosen else "path"
        if i in chosen:
            c -= weights[i - 1]
    marks[(n, W)] = "answer"
    ch.add(b.frame(f"Best value <strong>{dp[n][W]}</strong>. Walking back up: wherever a cell differs from the one above, "
                   f"that item was taken &mdash; items {sorted(chosen)} (weights "
                   f"{[weights[i-1] for i in sorted(chosen)]}).",
                   formula=f"answer = dp[{n}][{W}] = {dp[n][W]}", marks=marks))

    ch = s.chapter("One row, right to left")
    row = [0] * (W + 1)
    for i in range(n):
        w, v = weights[i], values[i]
        b = Board(1, W + 1, row_labels=["row"], col_labels=list(range(W + 1)))
        b.row(0, row, "done")
        ch.add(b.frame(f"Item {i + 1} (weight {w}, value {v}): sweep capacities from <strong>high to low</strong>, "
                       "so <code>row[c - w]</code> still holds the value from <em>before</em> this item.",
                       formula=f"for c in range({W}, {w - 1}, -1): row[c] = max(row[c], row[c-{w}] + {v})"))
        for c in range(W, w - 1, -1):
            old = row[c]
            row[c] = max(row[c], row[c - w] + v)
            b.set(0, c, row[c], "done")
            ch.add(b.frame(f"c = {c}: keep {old} or take item {i + 1} on top of row[{c - w}] = {row[c - w]}.",
                           formula=f"row[{c}] = max({old}, {row[c-w]} + {v}) = {row[c]}",
                           marks={(0, c): "cur", (0, c - w): "src"}, arrows=[(0, c - w, 0, c)]))
    b = Board(1, W + 1, row_labels=["row"], col_labels=list(range(W + 1)))
    b.row(0, row, "done")
    ch.add(b.frame("Going left to right would let an item use the row it already updated &mdash; taking it twice. "
                   f"Right to left keeps it 0/1. Same answer, <strong>{row[W]}</strong>, with one row.",
                   formula=f"answer = row[{W}] = {row[W]}", marks={(0, W): "answer"}))
    assert row[W] == dp[n][W]
    return s.build()


# ------------------------------------------------------------------ reachable-sums helper
def _reachable_rows(ch, nums, target, what):
    """One row per item: which sums 0..target are reachable using items so far."""
    n = len(nums)
    reach = [True] + [False] * target
    b = Board(n + 1, target + 1, row_labels=["start"] + [f"+{x}" for x in nums], col_labels=list(range(target + 1)))
    for c in range(target + 1):
        b.set(0, c, reach[c], "yes" if reach[c] else "no")
    ch.add(b.frame(f"Row <em>start</em>: with no {what} chosen, only the sum 0 is reachable.",
                   formula="reach = {0}"))
    for i, x in enumerate(nums, 1):
        new = reach[:]
        arrows = []
        for c in range(target, x - 1, -1):
            if reach[c - x] and not reach[c]:
                new[c] = True
                arrows.append((i - 1, c - x, i, c))
        for c in range(target + 1):
            b.set(i, c, new[c], "yes" if new[c] else "no")
        newly = [c for c in range(target + 1) if new[c] and not reach[c]]
        marks = {(i, c): "cur" for c in newly}
        ch.add(b.frame(f"Add {x}: every sum reachable before stays reachable (skip it), and every reachable sum + {x} "
                       f"becomes reachable (take it). New: {newly if newly else 'nothing'}.",
                       formula=f"reach |= {{s + {x} for s in reach}}", marks=marks, arrows=arrows[:8]))
        reach = new
    return b, reach


def partition_equal_subset_sum():
    nums = [1, 5, 11, 5]
    total = sum(nums)
    target = total // 2
    s = Story()
    ch = s.chapter("The question")
    b = Board(1, len(nums), row_labels=["nums"], col_labels=list(range(len(nums))), cls="")
    b.row(0, nums)
    ch.add(b.frame(f"Can the array be split into two groups with equal sums? The total is {total}, so each group "
                   f"must sum to {target}: the question becomes <strong>is there a subset summing to {target}?</strong>"))
    ch = s.chapter("Reachable sums")
    b, reach = _reachable_rows(ch, nums, target, "numbers")
    n = len(nums)
    ch.add(b.frame(f"After all numbers, sum {target} is " + ("<strong>reachable</strong>: e.g. 11 on one side and 1 + 5 + 5 on the other."
                                                          if reach[target] else "<strong>not</strong> reachable."),
                   formula=f"answer = reach[{target}] = {reach[target]}", marks={(n, target): "answer"}))
    return s.build()


def last_stone_weight_ii():
    stones = [2, 7, 4, 1, 8, 1]
    total = sum(stones)
    half = total // 2
    s = Story()
    ch = s.chapter("The question")
    b = Board(1, len(stones), row_labels=["stones"], col_labels=list(range(len(stones))), cls="")
    b.row(0, stones)
    ch.add(b.frame("Smash stones pairwise; the result is |a &minus; b|. Whatever the order, the final stone equals "
                   "(sum of one group) &minus; (sum of the other) for some split into two groups."))
    ch.add(b.frame(f"So make the groups as equal as possible: find the largest reachable subset sum &le; {total} / 2 = {half}. "
                   f"The answer is {total} &minus; 2 &times; that sum."))
    ch = s.chapter("Reachable sums")
    b, reach = _reachable_rows(ch, stones, half, "stones")
    best = max(c for c in range(half + 1) if reach[c])
    ch.add(b.frame(f"The largest reachable sum &le; {half} is <strong>{best}</strong>, so the smallest possible last stone is "
                   f"{total} &minus; 2 &times; {best} = <strong>{total - 2 * best}</strong>.",
                   formula=f"answer = {total} - 2*{best} = {total - 2 * best}", marks={(len(stones), best): "answer"}))
    return s.build()


# ------------------------------------------------------------------ target sum
def target_sum():
    nums, target = [1, 1, 1, 1, 1], 3
    n = len(nums)
    span = sum(nums)
    cols = list(range(-span, span + 1))
    s = Story()
    ch = s.chapter("Count the sign choices")
    ways = {0: 1}
    b = Board(n + 1, len(cols), row_labels=["start"] + [f"\u00b1{x}" for x in nums], col_labels=cols)
    for k, c in enumerate(cols):
        b.set(0, k, ways.get(c, ""), "base" if c in ways else "no")
    ch.add(b.frame(f"Put + or &minus; in front of every number. How many ways reach {target}? "
                   "Each column is a running sum; each cell counts the ways to reach it. Before any number: one way to have 0.",
                   formula="ways = {0: 1}"))
    for i, x in enumerate(nums, 1):
        new = {}
        for sm, w in ways.items():
            new[sm + x] = new.get(sm + x, 0) + w
            new[sm - x] = new.get(sm - x, 0) + w
        arrows, marks = [], {}
        for k, c in enumerate(cols):
            b.set(i, k, new.get(c, ""), "done" if c in new else "no")
            if c in new:
                marks[(i, k)] = "cur"
        for sm in ways:
            for d in (x, -x):
                arrows.append((i - 1, cols.index(sm), i, cols.index(sm + d)))
        ch.add(b.frame(f"Number {i} ({x}): every running sum s fans out to s + {x} and s &minus; {x}; counts that land on "
                       "the same sum add up.", formula="new[s + x] += ways[s];  new[s - x] += ways[s]",
                       marks=marks, arrows=arrows))
        ways = new
    k = cols.index(target)
    ch.add(b.frame(f"<strong>{ways.get(target, 0)} ways</strong> to reach {target}: choose which one of the five 1s is negative.",
                   formula=f"answer = ways[{target}] = {ways.get(target, 0)}", marks={(n, k): "answer"}))
    return s.build()


# ------------------------------------------------------------------ ones and zeroes
def ones_and_zeroes():
    strs, m, n = ["10", "0001", "111001", "1", "0"], 5, 3
    s = Story()
    ch = s.chapter("A two-capacity knapsack")
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    b = Board(m + 1, n + 1, row_labels=[f"{z} zeros" for z in range(m + 1)], col_labels=[f"{o} ones" for o in range(n + 1)])
    for z in range(m + 1):
        for o in range(n + 1):
            b.set(z, o, 0, "base")
    ch.add(b.frame(f"Pick as many strings as possible using at most {m} zeros and {n} ones in total. "
                   "<code>dp[z][o]</code> = most strings that fit in a budget of z zeros and o ones. Nothing picked yet: all 0.",
                   formula="dp[z][o] = 0"))
    for word in strs:
        zc, oc = word.count("0"), word.count("1")
        changed = []
        for z in range(m, zc - 1, -1):
            for o in range(n, oc - 1, -1):
                if dp[z - zc][o - oc] + 1 > dp[z][o]:
                    dp[z][o] = dp[z - zc][o - oc] + 1
                    changed.append((z, o))
        for z in range(m + 1):
            for o in range(n + 1):
                b.set(z, o, dp[z][o], "done")
        ex = changed[0] if changed else None
        ch.add(b.frame(f"String <code>{word}</code> costs {zc} zero{'s' * (zc != 1)} and {oc} one{'s' * (oc != 1)}. For every budget that can afford it, "
                       f"compare skipping it with taking it on top of <code>dp[z-{zc}][o-{oc}]</code>. "
                       f"{len(changed)} cell{'s' * (len(changed) != 1)} improved. Budgets are swept from high to low, as in 0/1 knapsack.",
                       formula=f"dp[z][o] = max(dp[z][o], dp[z-{zc}][o-{oc}] + 1)",
                       marks={c: "cur" for c in changed},
                       arrows=[(ex[0] - zc, ex[1] - oc, ex[0], ex[1])] if ex and (zc or oc) else None))
    ch.add(b.frame(f"With the full budget of {m} zeros and {n} ones, at most <strong>{dp[m][n]}</strong> strings fit "
                   "(e.g. 10, 0001, 1, 0).", formula=f"answer = dp[{m}][{n}] = {dp[m][n]}", marks={(m, n): "answer"}))
    return s.build()


# ------------------------------------------------------------------ coin change
def coin_change():
    coins, amount = [1, 2, 5], 11
    s = Story()
    t = CallTrace()
    small = 7

    def f(a):
        with t.call(a):
            if a == 0:
                return 0
            return min((f(a - c) + 1 for c in coins if c <= a), default=inf)

    f(small)
    heat_chapter(
        s, "Plain recursion repeats work", t,
        lambda: Board(1, small + 1, row_labels=["calls"], col_labels=list(range(small + 1))),
        lambda k: (0, k),
        f"Fewest coins for amount a = 1 + fewest coins for (a &minus; c), for the best coin c. "
        f"As plain recursion on amount {small}:",
        lambda k, n: f"Call <code>fewest({k})</code>; computed {n}&times; so far.",
        lambda calls, counts: f"<strong>{calls} calls</strong> for only {len(counts)} distinct amounts. "
                              f"Amount 1 alone was solved {counts.get(1, 0)} times.")

    ch = s.chapter("Fill the table")
    dp = [0] + [inf] * amount
    b = Board(1, amount + 1, row_labels=["coins"], col_labels=list(range(amount + 1)))
    b.set(0, 0, 0, "base")
    ch.add(b.frame(f"<code>dp[a]</code> = fewest coins (from {coins}) that make amount a. Zero coins make amount 0.",
                   formula="dp[0] = 0"))
    for a in range(1, amount + 1):
        options = {c: dp[a - c] + 1 for c in coins if c <= a}
        dp[a] = min(options.values(), default=inf)
        b.set(0, a, dp[a], "done")
        best_c = min(options, key=lambda c: (options[c], -c))
        marks = {(0, a): "cur"}
        for c in options:
            marks[(0, a - c)] = "src"
        ch.add(b.frame(f"Amount {a}: try the last coin being " +
                       ", ".join(f"{c} (1 + dp[{a - c}])" for c in options) +
                       f". Best: coin {best_c}.",
                       formula=f"dp[{a}] = min(" + ", ".join(f"{fmt(dp[a - c])}+1" for c in options) + f") = {fmt(dp[a])}",
                       marks=marks, arrows=[(0, a - c, 0, a) for c in options]))
    path, a = [], amount
    while a:
        c = min((c for c in coins if c <= a and dp[a - c] + 1 == dp[a]), key=lambda c: -c)
        path.append(c); a -= c
    marks = {(0, amount): "answer"}
    a = amount
    for c in path:
        a -= c
        marks[(0, a)] = "chosen"
    ch.add(b.frame(f"<strong>{dp[amount]} coins</strong> make {amount}: {' + '.join(map(str, path))}. Following the "
                   "chosen coins back from 11 visits the highlighted amounts.",
                   formula=f"answer = dp[{amount}] = {dp[amount]}", marks=marks))
    return s.build()


def coin_change_ii():
    coins, amount = [1, 2, 5], 5
    s = Story()
    ch = s.chapter("Count combinations, coin by coin")
    rows = [[1] + [0] * amount]
    b = Board(len(coins) + 1, amount + 1, row_labels=["none"] + [f"+coin {c}" for c in coins], col_labels=list(range(amount + 1)))
    b.row(0, rows[0], "base")
    ch.add(b.frame("Count the <em>combinations</em> (order does not matter) that make each amount. Row k uses only the first k coin "
                   "types. With no coins, only amount 0 can be made, in one way.",
                   formula="ways[0] = 1"))
    for i, c in enumerate(coins, 1):
        row = rows[-1][:]
        for a in range(amount + 1):
            if a >= c:
                row[a] = rows[-1][a] + row[a - c]
            b.set(i, a, row[a], "done")
            marks, arrows = {(i, a): "cur", (i - 1, a): "src"}, [(i - 1, a, i, a)]
            if a >= c:
                marks[(i, a - c)] = "src"; arrows.append((i, a - c, i, a))
                why = (f"combinations without any {c}-coin ({rows[-1][a]}, above) plus combinations that use at least one "
                       f"{c}-coin ({row[a - c]}, left by {c})")
                formula = f"ways[{a}] = {rows[-1][a]} + {row[a - c]} = {row[a]}"
            else:
                why = f"a {c}-coin is too big, so copy the count from above"
                formula = f"ways[{a}] = {row[a]}"
            ch.add(b.frame(f"Coin {c}, amount {a}: {why}.", formula=formula, marks=marks, arrows=arrows))
        rows.append(row)
    ch.add(b.frame(f"<strong>{rows[-1][amount]}</strong> combinations make {amount}: 5, 2+2+1, 2+1+1+1, 1+1+1+1+1. "
                   "Looping coins on the outside is what stops 1+2 and 2+1 from being counted twice.",
                   formula=f"answer = {rows[-1][amount]}", marks={(len(coins), amount): "answer"}))
    return s.build()


def perfect_squares():
    n = 12
    s = Story()
    ch = s.chapter("Fill the table")
    squares = [k * k for k in range(1, isqrt(n) + 1)]
    dp = [0] + [inf] * n
    b = Board(1, n + 1, row_labels=["fewest"], col_labels=list(range(n + 1)))
    b.set(0, 0, 0, "base")
    ch.add(b.frame(f"Fewest perfect squares ({', '.join(map(str, squares))}) that sum to each number. "
                   "This is Coin Change where the coins are the squares.", formula="dp[0] = 0"))
    for i in range(1, n + 1):
        opts = {sq: dp[i - sq] + 1 for sq in squares if sq <= i}
        dp[i] = min(opts.values())
        b.set(0, i, dp[i], "done")
        best = min(opts, key=lambda q: (opts[q], -q))
        marks = {(0, i): "cur"}
        for q in opts:
            marks[(0, i - q)] = "src"
        ch.add(b.frame(f"{i}: the last square used could be " + ", ".join(map(str, opts)) +
                       f"; best is {best} on top of {i - best}.",
                       formula=f"dp[{i}] = min(" + ", ".join(f"dp[{i-q}]+1" for q in opts) + f") = {dp[i]}",
                       marks=marks, arrows=[(0, i - q, 0, i) for q in opts]))
    ch.add(b.frame(f"<strong>{dp[n]}</strong> squares make {n}: 4 + 4 + 4. Greedy (largest square first) would take 9 + 1 + 1 + 1 = 4 squares.",
                   formula=f"answer = dp[{n}] = {dp[n]}", marks={(0, n): "answer", (0, 8): "chosen", (0, 4): "chosen"}))
    return s.build()


BUILDERS = {
    "knapsack-01": knapsack_01,
    "partition-equal-subset-sum": partition_equal_subset_sum,
    "target-sum": target_sum,
    "last-stone-weight-ii": last_stone_weight_ii,
    "ones-and-zeroes": ones_and_zeroes,
    "coin-change": coin_change,
    "coin-change-ii": coin_change_ii,
    "perfect-squares": perfect_squares,
}
