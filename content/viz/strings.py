"""Animations for the two-string DP problems. Rows are prefixes of the first
string, columns prefixes of the second; the axis labels are the characters."""
from ._kit import Board, Story

E = "∅"          # empty prefix


def _board(a, b):
    return Board(len(a) + 1, len(b) + 1, row_labels=[E] + list(a), col_labels=[E] + list(b))


# ------------------------------------------------------------------ LCS
def longest_common_subsequence():
    a, b_ = "abcde", "ace"
    R, C = len(a) + 1, len(b_) + 1
    s = Story()
    ch = s.chapter("Fill the table")
    dp = [[0] * C for _ in range(R)]
    b = _board(a, b_)
    for i in range(R):
        b.set(i, 0, 0, "base")
    for j in range(C):
        b.set(0, j, 0, "base")
    ch.add(b.frame(f"<code>dp[i][j]</code> = length of the LCS of the first i letters of <code>{a}</code> and the first j "
                   f"letters of <code>{b_}</code>. Against an empty string the LCS is 0.", formula="dp[0][*] = dp[*][0] = 0"))
    for i in range(1, R):
        for j in range(1, C):
            x, y = a[i - 1], b_[j - 1]
            if x == y:
                dp[i][j] = dp[i - 1][j - 1] + 1
                b.set(i, j, dp[i][j], "done")
                ch.add(b.frame(f"'{x}' matches '{y}': extend the LCS of both strings without it by one.",
                               formula=f"dp[{i}][{j}] = dp[{i-1}][{j-1}] + 1 = {dp[i][j]}",
                               marks={(i, j): "cur", (i - 1, j - 1): "src"}, arrows=[(i - 1, j - 1, i, j)]))
            else:
                up, left = dp[i - 1][j], dp[i][j - 1]
                dp[i][j] = max(up, left)
                src = (i - 1, j) if up >= left else (i, j - 1)
                b.set(i, j, dp[i][j], "done")
                ch.add(b.frame(f"'{x}' &ne; '{y}': one of them is not in the LCS, so drop '{x}' (above, {up}) or drop '{y}' "
                               f"(left, {left}) and keep the better.",
                               formula=f"dp[{i}][{j}] = max({up}, {left}) = {dp[i][j]}",
                               marks={(i, j): "cur", (i - 1, j): "src", (i, j - 1): "src"},
                               arrows=[(src[0], src[1], i, j)]))
    i, j, path, out = R - 1, C - 1, [], []
    while i and j:
        path.append((i, j))
        if a[i - 1] == b_[j - 1]:
            out.append(a[i - 1]); i, j = i - 1, j - 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    marks = {p: "chosen" if a[p[0] - 1] == b_[p[1] - 1] else "path" for p in path}
    marks[(R - 1, C - 1)] = "answer"
    ch.add(b.frame(f"LCS length <strong>{dp[-1][-1]}</strong>. Walking back (diagonal on a match, otherwise toward the larger "
                   f"neighbour) spells <code>{''.join(reversed(out))}</code>.",
                   formula=f"answer = dp[{R-1}][{C-1}] = {dp[-1][-1]}", marks=marks, path=path[::-1]))
    return s.build()


# ------------------------------------------------------------------ Edit distance
def edit_distance():
    a, b_ = "horse", "ros"
    R, C = len(a) + 1, len(b_) + 1
    s = Story()
    ch = s.chapter("Fill the table")
    dp = [[0] * C for _ in range(R)]
    b = _board(a, b_)
    for i in range(R):
        dp[i][0] = i; b.set(i, 0, i, "base")
    for j in range(C):
        dp[0][j] = j; b.set(0, j, j, "base")
    ch.add(b.frame(f"<code>dp[i][j]</code> = fewest edits turning the first i letters of <code>{a}</code> into the first j letters "
                   f"of <code>{b_}</code>. From or to an empty string it is just that many deletes or inserts.",
                   formula="dp[i][0] = i,  dp[0][j] = j"))
    for i in range(1, R):
        for j in range(1, C):
            x, y = a[i - 1], b_[j - 1]
            if x == y:
                dp[i][j] = dp[i - 1][j - 1]
                b.set(i, j, dp[i][j], "done")
                ch.add(b.frame(f"'{x}' = '{y}': no edit needed, inherit the diagonal.",
                               formula=f"dp[{i}][{j}] = dp[{i-1}][{j-1}] = {dp[i][j]}",
                               marks={(i, j): "cur", (i - 1, j - 1): "src"}, arrows=[(i - 1, j - 1, i, j)]))
                continue
            opts = {"replace": dp[i - 1][j - 1], "delete": dp[i - 1][j], "insert": dp[i][j - 1]}
            op = min(opts, key=opts.get)
            dp[i][j] = 1 + opts[op]
            src = {"replace": (i - 1, j - 1), "delete": (i - 1, j), "insert": (i, j - 1)}[op]
            b.set(i, j, dp[i][j], "done")
            ch.add(b.frame(f"'{x}' &ne; '{y}': replace '{x}' with '{y}' (diagonal {opts['replace']}), delete '{x}' "
                           f"(above {opts['delete']}) or insert '{y}' (left {opts['insert']}). Cheapest: <strong>{op}</strong>.",
                           formula=f"dp[{i}][{j}] = 1 + min({opts['replace']}, {opts['delete']}, {opts['insert']}) = {dp[i][j]}",
                           marks={(i, j): "cur", (i - 1, j - 1): "src", (i - 1, j): "src", (i, j - 1): "src"},
                           arrows=[(src[0], src[1], i, j)]))
    i, j, path, ops = R - 1, C - 1, [(R - 1, C - 1)], []
    while i or j:
        if i and j and a[i - 1] == b_[j - 1] and dp[i][j] == dp[i - 1][j - 1]:
            i, j = i - 1, j - 1
        elif i and j and dp[i][j] == dp[i - 1][j - 1] + 1:
            ops.append(f"replace {a[i-1]}&rarr;{b_[j-1]}"); i, j = i - 1, j - 1
        elif i and dp[i][j] == dp[i - 1][j] + 1:
            ops.append(f"delete {a[i-1]}"); i -= 1
        else:
            ops.append(f"insert {b_[j-1]}"); j -= 1
        path.append((i, j))
    marks = {p: "path" for p in path}
    marks[(R - 1, C - 1)] = "answer"
    ch.add(b.frame(f"<strong>{dp[-1][-1]} edits</strong>: {', '.join(reversed(ops))}.",
                   formula=f"answer = dp[{R-1}][{C-1}] = {dp[-1][-1]}", marks=marks, path=path[::-1]))
    return s.build()


# ------------------------------------------------------------------ Distinct subsequences
def distinct_subsequences():
    a, t = "babgbag", "bag"
    R, C = len(a) + 1, len(t) + 1
    s = Story()
    ch = s.chapter("Fill the table")
    dp = [[0] * C for _ in range(R)]
    b = _board(a, t)
    for i in range(R):
        dp[i][0] = 1; b.set(i, 0, 1, "base")
    for j in range(1, C):
        b.set(0, j, 0, "base")
    ch.add(b.frame(f"<code>dp[i][j]</code> = number of ways the first j letters of <code>{t}</code> appear as a subsequence of the "
                   f"first i letters of <code>{a}</code>. The empty target appears exactly once in anything; a non-empty target "
                   "never appears in the empty string.", formula="dp[i][0] = 1,  dp[0][j>0] = 0"))
    for i in range(1, R):
        for j in range(1, C):
            x, y = a[i - 1], t[j - 1]
            skip = dp[i - 1][j]
            use = dp[i - 1][j - 1] if x == y else 0
            dp[i][j] = skip + use
            b.set(i, j, dp[i][j], "done")
            marks, arrows = {(i, j): "cur", (i - 1, j): "src"}, [(i - 1, j, i, j)]
            if x == y:
                marks[(i - 1, j - 1)] = "src"; arrows.append((i - 1, j - 1, i, j))
                why = f"'{x}' matches '{y}': ways that skip this '{x}' ({skip}) plus ways that use it to finish '{t[:j]}' ({use})."
            else:
                why = f"'{x}' &ne; '{y}': this letter cannot help, so only the ways without it ({skip})."
            ch.add(b.frame(why, formula=f"dp[{i}][{j}] = {skip} + {use} = {dp[i][j]}" if x == y else f"dp[{i}][{j}] = {skip}",
                           marks=marks, arrows=arrows))
    ch.add(b.frame(f"<code>{t}</code> appears <strong>{dp[-1][-1]}</strong> times as a subsequence of <code>{a}</code>.",
                   formula=f"answer = {dp[-1][-1]}", marks={(R - 1, C - 1): "answer"}))
    return s.build()


# ------------------------------------------------------------------ Longest palindromic subsequence
def longest_palindromic_subsequence():
    w = "bbbab"
    n = len(w)
    s = Story()
    ch = s.chapter("Fill by interval length")
    dp = [[0] * n for _ in range(n)]
    b = Board(n, n, row_labels=[f"{i}:{c}" for i, c in enumerate(w)], col_labels=[f"{j}:{c}" for j, c in enumerate(w)])
    for i in range(n):
        for j in range(i):
            b.set(i, j, "", "none")
    for i in range(n):
        dp[i][i] = 1; b.set(i, i, 1, "base")
    ch.add(b.frame(f"<code>dp[i][j]</code> = longest palindromic subsequence of <code>{w}[i..j]</code>. Only i &le; j matters. "
                   "A single letter is a palindrome of length 1.", formula="dp[i][i] = 1"))
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if w[i] == w[j]:
                inner = dp[i + 1][j - 1] if length > 2 else 0
                dp[i][j] = inner + 2
                b.set(i, j, dp[i][j], "done")
                marks, arrows = {(i, j): "cur"}, []
                if length > 2:
                    marks[(i + 1, j - 1)] = "src"; arrows.append((i + 1, j - 1, i, j))
                ch.add(b.frame(f"<code>{w[i:j+1]}</code>: the ends '{w[i]}' and '{w[j]}' match, so wrap them around the best "
                               f"palindrome inside ({inner}).",
                               formula=f"dp[{i}][{j}] = dp[{i+1}][{j-1}] + 2 = {dp[i][j]}" if length > 2 else f"dp[{i}][{j}] = 2",
                               marks=marks, arrows=arrows))
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
                b.set(i, j, dp[i][j], "done")
                ch.add(b.frame(f"<code>{w[i:j+1]}</code>: ends differ, so drop one end: without '{w[i]}' ({dp[i+1][j]}) or "
                               f"without '{w[j]}' ({dp[i][j-1]}).",
                               formula=f"dp[{i}][{j}] = max({dp[i+1][j]}, {dp[i][j-1]}) = {dp[i][j]}",
                               marks={(i, j): "cur", (i + 1, j): "src", (i, j - 1): "src"},
                               arrows=[(i + 1, j, i, j), (i, j - 1, i, j)]))
    ch.add(b.frame(f"The whole string is the top-right cell: <strong>{dp[0][n-1]}</strong> (<code>bbbb</code>). Intervals are "
                   "filled shortest first, so every inner interval is ready when needed.",
                   formula=f"answer = dp[0][{n-1}] = {dp[0][n-1]}", marks={(0, n - 1): "answer"}))
    return s.build()


# ------------------------------------------------------------------ Interleaving string
def interleaving_string():
    s1, s2, s3 = "aab", "axy", "aaxaby"
    R, C = len(s1) + 1, len(s2) + 1
    s = Story()
    ch = s.chapter("Fill the table")
    dp = [[False] * C for _ in range(R)]
    b = _board(s1, s2)
    dp[0][0] = True
    b.set(0, 0, True, "yes")
    ch.add(b.frame(f"Is <code>{s3}</code> an interleaving of <code>{s1}</code> and <code>{s2}</code>? "
                   f"<code>dp[i][j]</code> = can the first i letters of s1 and j letters of s2 form the first i + j letters of s3. "
                   "Two empty prefixes form the empty string.", formula="dp[0][0] = True"))
    for i in range(R):
        for j in range(C):
            if i == 0 and j == 0:
                continue
            k = i + j - 1
            from_up = i > 0 and dp[i - 1][j] and s1[i - 1] == s3[k]
            from_left = j > 0 and dp[i][j - 1] and s2[j - 1] == s3[k]
            dp[i][j] = from_up or from_left
            b.set(i, j, dp[i][j], "yes" if dp[i][j] else "no")
            marks, arrows = {(i, j): "cur"}, []
            parts = []
            if i:
                marks[(i - 1, j)] = "src"
                parts.append(f"take '{s1[i-1]}' from s1 (needs dp[{i-1}][{j}] = {dp[i-1][j]} and '{s1[i-1]}' = s3[{k}] '{s3[k]}')")
                if from_up: arrows.append((i - 1, j, i, j))
            if j:
                marks[(i, j - 1)] = "src"
                parts.append(f"take '{s2[j-1]}' from s2 (needs dp[{i}][{j-1}] = {dp[i][j-1]} and '{s2[j-1]}' = s3[{k}] '{s3[k]}')")
                if from_left: arrows.append((i, j - 1, i, j))
            ch.add(b.frame("Either " + " or ".join(parts) + ".", formula=f"dp[{i}][{j}] = {dp[i][j]}",
                           marks=marks, arrows=arrows))
    ch.add(b.frame(f"<code>{s3}</code> " + ("<strong>is</strong>" if dp[-1][-1] else "is <strong>not</strong>") +
                   f" an interleaving. Every True cell is a way to have used some of each string so far.",
                   formula=f"answer = dp[{R-1}][{C-1}] = {dp[-1][-1]}", marks={(R - 1, C - 1): "answer"}))
    return s.build()


BUILDERS = {
    "longest-common-subsequence": longest_common_subsequence,
    "edit-distance": edit_distance,
    "distinct-subsequences": distinct_subsequences,
    "longest-palindromic-subsequence": longest_palindromic_subsequence,
    "interleaving-string": interleaving_string,
}
