"""Write-ups for Dynamic Programming, part 6: interval problems."""

EXPLAIN = {
    # ------------------------------------------------------------------ palindromic substrings
    "palindromic-substrings": {
        "example": {"call": 'count_substrings("abba")', "expect": "6"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "<code>s[i..j]</code> is a palindrome when its ends match and the inside <code>s[i+1..j-1]</code> is a palindrome.",
                    "Test every range with that recursion and count the ones that pass.",
                ],
                "steps": [
                    "<code>pal(i, j)</code> is True when i ≥ j (empty or one character).",
                    "Sum over all i ≤ j.",
                ],
                "why": [
                    "Each test walks inwards in up to n/2 steps, and there are n²/2 ranges: O(n³).",
                ],
                "dry": [
                    "Single letters give 4 palindromes: a, b, b, a.",
                    "\"bb\" passes; \"abba\" passes (a = a and \"bb\" is a palindrome). \"ab\", \"abb\", \"bba\" and \"ba\" fail.",
                    "The total is <strong>6</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<code>pal(i, j)</code> depends on <code>pal(i+1, j-1)</code>, which other ranges also need. Cache it.",
                ],
                "steps": [
                    "<code>@cache</code> on pal.",
                ],
                "why": [
                    "It is O(n²): each range is decided once in O(1).",
                ],
                "dry": [
                    "pal(0, 3) reuses pal(1, 2) = True, which was already found when counting \"bb\".",
                    "The total is <strong>6</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<code>pal[i][j]</code> reads <code>pal[i+1][j-1]</code>, in the row below, so fill i from n-1 down to 0.",
                    "Lengths 1 and 2 (<code>j - i &lt; 2</code>) have no inside to check.",
                ],
                "steps": [
                    "Count every True cell as it is set.",
                ],
                "why": [
                    "It is O(n²) time and space.",
                ],
                "dry": [
                    "i = 3: {3}. i = 2: {2}. i = 1: {1, 2} (\"bb\").",
                    "i = 0: {0, 3} (\"abba\", since pal[1][2] is True).",
                    "The count is 1 + 1 + 2 + 2 = <strong>6</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only row i+1 (<code>below</code>).",
                ],
                "steps": [
                    "<code>cur[j] = s[i] == s[j] and (j - i &lt; 2 or below[j-1])</code>.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "Same rows as the table.",
                    "The count is <strong>6</strong>.",
                ],
            },
            "One row, j right to left": {
                "idea": [
                    "Cell j reads only j-1 of the row below: the cell to its left.",
                    "Sweeping j from right to left means j-1 has not been overwritten yet, so it still holds the row below.",
                ],
                "steps": [
                    "<code>pal[j] = s[i] == s[j] and (j - i &lt; 2 or pal[j-1])</code>; add it to the count.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "At i = 0: j = 3 reads pal[2], which still holds row 1's value (True, from \"bb\"), so \"abba\" counts.",
                    "The total is <strong>6</strong>.",
                ],
            },
            "Expand around each centre": {
                "idea": [
                    "Every palindrome has a centre: a character (odd length) or a gap between two (even length). There are 2n - 1 centres.",
                    "From each centre, expand outwards while the ends match, counting one palindrome per step.",
                ],
                "steps": [
                    "<code>lo, hi = c // 2, (c + 1) // 2</code>; expand while <code>s[lo] == s[hi]</code>.",
                ],
                "why": [
                    "It is O(n²) time and O(1) space: the same recurrence read from the inside out.",
                ],
                "dry": [
                    "Each letter as a centre gives 1, so 4 in total.",
                    "The gap between the two b's gives \"bb\", then \"abba\": 2 more. Other gaps give 0.",
                    "The total is <strong>6</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest palindromic substring
    "longest-palindromic-substring": {
        "example": {"call": 'longest_palindrome("bananas")', "expect": "'anana'"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Test every range with the inward-walking palindrome check, and keep the widest that passes.",
                    "Skip ranges no wider than the current best; it is faster in practice, but the worst case is the same.",
                ],
                "steps": [
                    "Track <code>lo, hi</code> of the best; return <code>s[lo:hi]</code>.",
                ],
                "why": [
                    "It is O(n³).",
                ],
                "dry": [
                    "The palindromes longer than 2 are \"ana\", \"nan\", \"ana\" and \"anana\".",
                    "The widest is <strong>'anana'</strong> (indices 1–5).",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>pal(i, j)</code> so each range is decided once.",
                ],
                "steps": [
                    "<code>@cache</code> on pal.",
                ],
                "why": [
                    "It is O(n²) time and space.",
                ],
                "dry": [
                    "pal(1, 5) = a == a and pal(2, 4) (\"nan\") = True.",
                    "The result is <strong>'anana'</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "This is the Palindromic Substrings table, but it records the widest True cell instead of counting.",
                ],
                "steps": [
                    "Fill i downwards and j upwards.",
                ],
                "why": [
                    "It is O(n²) time and space.",
                ],
                "dry": [
                    "At i = 3, pal[3][5] (\"ana\") is True. At i = 2, pal[2][4] (\"nan\") is True.",
                    "At i = 1, pal[1][5] (\"anana\") is True, so the best becomes width 5.",
                    "The result is <strong>'anana'</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only row i+1.",
                ],
                "steps": [
                    "As in the table, with <code>below</code>.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "The result is <strong>'anana'</strong>.",
                ],
            },
            "One row, j right to left": {
                "idea": [
                    "The only cell read is the one to the left, which a right-to-left sweep has not reached yet.",
                ],
                "steps": [
                    "Same update as Palindromic Substrings; track the widest.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "At i = 1 and j = 5, pal[4] still holds row 2's \"nan\" = True.",
                    "The result is <strong>'anana'</strong>.",
                ],
            },
            "Expand around each centre": {
                "idea": [
                    "Expand from each of the 2n - 1 centres and remember the widest window.",
                    "The loop overshoots by one on each side, so the palindrome is <code>s[lo+1:hi]</code>.",
                ],
                "steps": [
                    "Compare <code>hi - lo - 1</code> with the best width.",
                ],
                "why": [
                    "It is O(n²) time and O(1) space. Manacher's algorithm does it in O(n).",
                ],
                "dry": [
                    "The centre at index 3 ('a'): n = n, a = a, then b ≠ s stops.",
                    "Width 5: <strong>'anana'</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ matrix chain
    "matrix-chain-multiplication": {
        "example": {"call": "matrix_chain_order([40, 20, 30, 10, 30])", "expect": "26000"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Some multiplication is done last: it joins (i..k) and (k+1..j) for some split k.",
                    "Its cost is <code>arr[i-1]·arr[k]·arr[j]</code>, plus the best cost of each side.",
                    "Try every k and take the minimum.",
                ],
                "steps": [
                    "<code>cost(i, i) = 0</code>; call <code>cost(1, n)</code>.",
                ],
                "why": [
                    "It tries every bracketing, a Catalan number of them, about 4<sup>n</sup>.",
                ],
                "dry": [
                    "The matrices are A1 40×20, A2 20×30, A3 30×10 and A4 10×30.",
                    "The best is ((A1(A2A3))A4): 6000 + 8000 + 12000.",
                    "The total is <strong>26000</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Different outer bracketings share the same inner ranges. Cache each <code>(i, j)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on cost.",
                ],
                "why": [
                    "There are n² ranges, each trying up to n splits: O(n³).",
                ],
                "dry": [
                    "cost(1, 3) = 14000 is used by the split k = 3 of cost(1, 4).",
                    "cost(1, 4) = 14000 + 0 + 40·10·30 = <strong>26000</strong>.",
                ],
            },
            "Bottom-up by length": {
                "idea": [
                    "Every split produces strictly shorter chains, so fill by chain length: 2, 3, …, n.",
                    "There is no row-saving trick here: a cell reads its whole row and its whole column.",
                ],
                "steps": [
                    "<code>dp[i][j] = min over k of dp[i][k] + dp[k+1][j] + arr[i-1]·arr[k]·arr[j]</code>.",
                ],
                "why": [
                    "It is O(n³) time and O(n²) space.",
                ],
                "dry": [
                    "Length 2: dp[1][2] = 24000, dp[2][3] = 6000, dp[3][4] = 9000.",
                    "Length 3: dp[1][3] = 14000 (k = 1), dp[2][4] = 12000 (k = 3).",
                    "Length 4: dp[1][4] = 26000 (k = 3). The result is <strong>26000</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ burst balloons
    "burst-balloons": {
        "example": {"call": "max_coins([3, 1, 5, 8])", "expect": "167"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Choosing the <em>first</em> balloon to burst changes everyone's neighbours, so it does not split the problem.",
                    "Choose the <em>last</em> balloon k to burst between the walls l and r. Its neighbours are then exactly the walls l and r, and the two sides are independent.",
                    "Pad the list with 1s at both ends as permanent walls.",
                ],
                "steps": [
                    "<code>best(l, r) = max over k of best(l, k) + v[l]·v[k]·v[r] + best(k, r)</code>.",
                ],
                "why": [
                    "Without a cache, shared ranges are re-solved again and again: exponential.",
                ],
                "dry": [
                    "vals = [1, 3, 1, 5, 8, 1].",
                    "Burst order 1, 5, 3, 8 gives 15 + 120 + 24 + 8.",
                    "The total is <strong>167</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>best(l, r)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on best.",
                ],
                "why": [
                    "It is O(n³).",
                ],
                "dry": [
                    "best(0, 5): the last balloon is 8, so best(0, 4) + 1·8·1 = 159 + 8.",
                    "The result is <strong>167</strong>.",
                ],
            },
            "Bottom-up by gap": {
                "idea": [
                    "Both sub-ranges have a smaller gap, so fill by gap = r - l from 2 upwards.",
                ],
                "steps": [
                    "<code>dp[l][r]</code> = the max over the last balloon k.",
                ],
                "why": [
                    "It is O(n³) time and O(n²) space, with no smaller version, as in Matrix Chain.",
                ],
                "dry": [
                    "dp[1][3] = 15 (burst 1 between 3 and 5); dp[1][4] = 15 + 3·5·8 = 135.",
                    "dp[0][4] = 1·3·8 + 135 = 159 (3 is last).",
                    "dp[0][5] = 159 + 1·8·1 = <strong>167</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ cut a stick
    "minimum-cost-to-cut-a-stick": {
        "example": {"call": "min_cost(7, [1, 3, 4, 5])", "expect": "16"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Sort the cuts and add both ends: pos = [0, 1, 3, 4, 5, 7].",
                    "For the piece between pos[i] and pos[j], the first cut k costs the piece's length, then splits it into (i, k) and (k, j).",
                ],
                "steps": [
                    "<code>cost(i, j) = pos[j] - pos[i] + min over k of cost(i, k) + cost(k, j)</code>; 0 if no cut is inside.",
                ],
                "why": [
                    "It tries every cut order: exponential.",
                ],
                "dry": [
                    "Cut at 3 (cost 7), then at 1 (cost 3), then at 5 (cost 4), then at 4 (cost 2).",
                    "The total is <strong>16</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>(i, j)</code> pieces.",
                ],
                "steps": [
                    "<code>@cache</code> on cost.",
                ],
                "why": [
                    "It is O(m³) for m positions.",
                ],
                "dry": [
                    "cost(0, 5) = 7 + cost(0, 2) + cost(2, 5) = 7 + 3 + 6.",
                    "The result is <strong>16</strong>.",
                ],
            },
            "Bottom-up by gap": {
                "idea": [
                    "Both pieces of any split have a smaller gap, so fill by gap from 2 upwards.",
                ],
                "steps": [
                    "<code>dp[i][j] = length + min over k of dp[i][k] + dp[k][j]</code>.",
                ],
                "why": [
                    "It is O(m³) time and O(m²) space.",
                ],
                "dry": [
                    "Gap 2: 3, 3, 2, 3. Gap 3: dp[0][3] = 7, dp[1][4] = 6, dp[2][5] = 6.",
                    "Gap 4: dp[0][4] = 10, dp[1][5] = 12.",
                    "Gap 5: dp[0][5] = 7 + min(…) = <strong>16</strong>.",
                ],
            },
        },
    },
}
