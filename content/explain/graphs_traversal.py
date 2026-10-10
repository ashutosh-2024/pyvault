"""Write-ups for the Graphs topic, part 1: traversal problems."""

CLONE_BASE = ("class Node:\n"
              "    def __init__(self, val=0, neighbors=None):\n"
              "        self.val = val\n"
              "        self.neighbors = neighbors if neighbors is not None else []\n"
              "def dump(start):                       # (value, neighbour values, is an original node?)\n"
              "    seen, stack, out = {start}, [start], []\n"
              "    while stack:\n"
              "        x = stack.pop()\n"
              "        out.append((x.val, sorted(y.val for y in x.neighbors), x in originals))\n"
              "        for y in x.neighbors:\n"
              "            if y not in seen:\n"
              "                seen.add(y)\n"
              "                stack.append(y)\n"
              "    return sorted(out)\n")

CLONE_SETUP = (CLONE_BASE +
               "n1, n2, n3, n4 = Node(1), Node(2), Node(3), Node(4)      # a square: 1-2-3-4-1\n"
               "n1.neighbors, n2.neighbors, n3.neighbors, n4.neighbors = [n2, n4], [n1, n3], [n2, n4], [n1, n3]\n"
               "originals = {n1, n2, n3, n4}\n"
               "copy = clone_graph(n1)")

CLONE_SETUP_2 = (CLONE_BASE +
                 "n1, n2 = Node(1), Node(2)      # two nodes pointing at each other\n"
                 "n1.neighbors, n2.neighbors = [n2], [n1]\n"
                 "originals = {n1, n2}\n"
                 "copy = clone_graph(n1)")

EXPLAIN = {
    # ------------------------------------------------------------------ island perimeter
    "island-perimeter": {
        "examples": [
            {"call": "island_perimeter([[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [1, 1, 0, 0]])", "expect": "16"},
            {"call": "island_perimeter([[1, 1, 1], [1, 0, 1], [1, 1, 1]])", "expect": "16"},
        ],
        "approaches": {
            "DFS, counting edges that face water or the border": {
                "idea": [
                    "The perimeter is the number of cell sides where land touches water or the edge of the grid.",
                    "Visit every land cell of the island once and, for each, count its sides that step into water or off the grid.",
                    "Sides shared with other land are not perimeter; those neighbours are pushed for visiting instead.",
                ],
                "steps": [
                    "Find the first land cell <code>start</code> and put it in <code>seen</code> and on <code>stack</code>.",
                    "Pop a cell <code>(r, c)</code> and look at its four neighbours <code>(nr, nc)</code>.",
                    "If the neighbour is off the grid or <code>grid[nr][nc] == 0</code>, add 1 to <code>perimeter</code>.",
                    "Otherwise it is land: if not yet in <code>seen</code>, mark it and push it.",
                    "When the stack is empty, every island cell has been processed: return <code>perimeter</code>.",
                ],
                "why": [
                    "Each land cell is popped exactly once (it is marked before being pushed), and each of its four sides is classified once, so every perimeter edge is counted exactly once.",
                    "Finding <code>start</code> and the traversal together touch each cell a constant number of times: <strong>O(m · n)</strong> time.",
                    "<code>seen</code> and <code>stack</code> can hold every land cell: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "start = (0,1): water above, left, right, so perimeter = 3; push (1,1).",
                        "(1,1) has land on all four sides: +0; push (1,0), (1,2), (2,1).",
                        "(1,0) +3 → 6, (1,2) +3 → 9, (2,1) +2 → 11 and pushes (3,1).",
                        "(3,1) +2 → 13 and pushes (3,0); (3,0) +3 → 16.",
                        "The stack is empty. The result is <strong>16</strong>.",
                    ],
                    [
                        "A ring of 8 land cells around a water cell. start = (0,0) +2 (top, left).",
                        "Every ring cell has exactly two land neighbours and two water or border sides, so each adds 2.",
                        "The sides facing the centre water cell count too: (0,1), (1,0), (1,2), (2,1) each have one of them.",
                        "8 cells × 2 = <strong>16</strong>: 12 outer edges plus 4 around the lake.",
                    ],
                ],
                "faq": [
                    ["Why can a single traversal from one start cell be enough?",
                     "The problem guarantees exactly one island, so every land cell is reachable from any other."],
                    ["Does a lake inside the island count?",
                     "Yes. The perimeter counts every land-water side, so the edges around an enclosed water cell are added, as the second example shows."],
                    ["Why mark cells when pushing rather than when popping?",
                     "Marking on push means a cell can never be on the stack twice, so it is processed once. Marking on pop would also be correct here if you skipped already-seen pops, but would push duplicates."],
                ],
            },
            "Count lands and shared edges": {
                "idea": [
                    "Each land cell contributes 4 sides. Every pair of adjacent land cells hides 2 of those sides, one from each.",
                    "So perimeter = <code>4 · lands − 2 · shared</code>, where <code>shared</code> counts adjacent land pairs.",
                    "Count each pair once by looking only down and right from each cell.",
                ],
                "steps": [
                    "Set <code>lands = shared = 0</code>.",
                    "For every cell with <code>v == 1</code>, add 1 to <code>lands</code>.",
                    "If the cell below is land, add 1 to <code>shared</code>.",
                    "If the cell to the right is land, add 1 to <code>shared</code>.",
                    "Return <code>4 * lands - 2 * shared</code>.",
                ],
                "why": [
                    "Every land-land adjacency is vertical or horizontal and is seen exactly once from its upper or left cell, so <code>shared</code> is exact.",
                    "Each shared side removes 2 from the naive 4-per-cell total, leaving exactly the land-water and land-border sides.",
                    "One pass over the grid: <strong>O(m · n)</strong> time. Two counters: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Land cells: (0,1), (1,0), (1,1), (1,2), (2,1), (3,0), (3,1): lands = 7.",
                        "Down pairs: (0,1)-(1,1), (1,1)-(2,1), (2,1)-(3,1). Right pairs: (1,0)-(1,1), (1,1)-(1,2), (3,0)-(3,1).",
                        "shared = 6.",
                        "4 · 7 − 2 · 6 = <strong>16</strong>.",
                    ],
                    [
                        "lands = 8 (the centre is water).",
                        "Right pairs: two in the top row, two in the bottom row. Down pairs: two in the left column, two in the right column. shared = 8.",
                        "4 · 8 − 2 · 8 = <strong>16</strong>.",
                    ],
                ],
                "faq": [
                    ["Why subtract <code>2 * shared</code> and not <code>shared</code>?",
                     "One shared edge removes a side from both cells that touch it, so it reduces the 4-per-cell total by 2."],
                    ["Why only look down and right?",
                     "Looking in all four directions would see each pair twice. Down and right sees each pair from exactly one end."],
                    ["Does this work with several islands?",
                     "Yes, it would return the total perimeter of all of them, since it never uses connectivity."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ verifying an alien dictionary
    "verify-alien-dictionary": {
        "examples": [
            {"call": "is_alien_sorted([\"word\", \"world\", \"row\"], \"worldabcefghijkmnpqstuvxyz\")", "expect": "False"},
            {"call": "is_alien_sorted([\"hello\", \"leetcode\"], \"hlabcdefgijkmnopqrstuvwxyz\")", "expect": "True"},
        ],
        "approaches": {
            "Translate to English letters, compare with sorted": {
                "idea": [
                    "Rename each alien letter to the English letter at the same rank: the first alien letter becomes 'a', the second 'b', and so on.",
                    "After renaming, alien order is ordinary string order, so Python's own comparison and <code>sorted</code> do the work.",
                ],
                "steps": [
                    "Build <code>to_english</code>: <code>order[i]</code> maps to <code>chr(97 + i)</code>.",
                    "Translate every word letter by letter into <code>translated</code>.",
                    "Sort a copy with <code>sorted(translated)</code>.",
                    "Return whether the translated list already equals its sorted version.",
                ],
                "why": [
                    "The renaming is order-preserving letter by letter, and string comparison is lexicographic, so word order is preserved exactly, including the rule that a prefix comes first.",
                    "Translating costs O(C) for C total characters; sorting n words costs <strong>O(C log n)</strong> comparisons-worth of character work.",
                    "The translated words take <strong>O(C)</strong> space.",
                ],
                "dry": [
                    [
                        "Ranks: w→a, o→b, r→c, l→d, d→e.",
                        "\"word\" → \"abce\", \"world\" → \"abcde\", \"row\" → \"cba\".",
                        "sorted gives [\"abcde\", \"abce\", \"cba\"], which differs from the original order.",
                        "The result is <strong>False</strong>.",
                    ],
                    [
                        "h→a, l→b, then a→c, b→d, c→e, d→f, e→g, …",
                        "\"hello\" → \"agbbo\", \"leetcode\" → \"bggteofg\".",
                        "\"agbbo\" &lt; \"bggteofg\", so the list is already sorted.",
                        "The result is <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does a prefix still sort first after translation?",
                     "Python compares strings so that a proper prefix is smaller, which matches the dictionary rule the problem uses."],
                    ["Why is this slower than checking neighbours?",
                     "Sorting does O(n log n) comparisons, while sortedness only needs the n − 1 adjacent pairs."],
                    ["Could I use <code>sorted(words, key=...)</code> instead of translating?",
                     "Yes: <code>key=lambda w: [rank[c] for c in w]</code> compares rank lists the same way. It is still a full sort."],
                ],
            },
            "Rank map, compare adjacent pairs": {
                "idea": [
                    "A list is sorted if every word is ≤ the next one, so only adjacent pairs need checking.",
                    "Two words are ordered by their first differing letter, compared with a rank table built from <code>order</code>.",
                    "If one word is a prefix of the other, the shorter must come first.",
                ],
                "steps": [
                    "Build <code>rank</code>: letter → position in <code>order</code>.",
                    "For each adjacent pair <code>(a, b)</code>, walk their letters together with <code>zip</code>.",
                    "At the first <code>x != y</code>: if <code>rank[x] &gt; rank[y]</code>, return <code>False</code>; otherwise the pair is fine, so <code>break</code>.",
                    "If the loop ends without a difference (the <code>else</code> of the <code>for</code>), the shorter is a prefix: return <code>False</code> if <code>len(a) &gt; len(b)</code>.",
                    "If all pairs pass, return <code>True</code>.",
                ],
                "why": [
                    "Lexicographic order is transitive, so checking each adjacent pair is enough for the whole list.",
                    "Each character is compared at most once per pair it belongs to, at most twice overall: <strong>O(C)</strong> time.",
                    "<code>rank</code> has at most 26 entries: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "rank: w=0, o=1, r=2, l=3, d=4.",
                        "Pair (\"word\", \"world\"): w, o, r match; then d vs l.",
                        "rank[d] = 4 &gt; rank[l] = 3, so \"word\" should come after \"world\".",
                        "The result is <strong>False</strong>, without looking at \"row\".",
                    ],
                    [
                        "rank: h=0, l=1.",
                        "Pair (\"hello\", \"leetcode\"): the first letters already differ, h vs l.",
                        "rank[h] = 0 &lt; rank[l] = 1: this pair is in order, so break.",
                        "No more pairs. The result is <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["What does the <code>for ... else</code> do here?",
                     "The <code>else</code> runs only when the loop finished without <code>break</code>, which means <code>zip</code> found no differing letter in the shorter length: one word is a prefix of the other."],
                    ["Why is <code>[\"apple\", \"app\"]</code> unsorted?",
                     "All three letters of \"app\" match, and \"apple\" is longer, so the prefix comes second. The <code>len(a) &gt; len(b)</code> check returns <code>False</code>."],
                    ["Why <code>break</code> after a correctly ordered difference?",
                     "Only the first differing letter decides the order; later letters do not matter."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find the town judge
    "find-town-judge": {
        "examples": [
            {"call": "find_judge(4, [[1, 3], [1, 4], [2, 3], [2, 4], [4, 3]])", "expect": "3"},
            {"call": "find_judge(3, [[1, 3], [2, 3], [3, 1]])", "expect": "-1"},
        ],
        "approaches": {
            "Check each candidate against all trust pairs": {
                "idea": [
                    "The judge trusts nobody and is trusted by all other n − 1 people.",
                    "Test each person against both conditions by scanning the trust list.",
                ],
                "steps": [
                    "Loop <code>p</code> from 1 to <code>n</code>.",
                    "If any pair has <code>a == p</code>, <code>p</code> trusts someone: skip.",
                    "Count pairs with <code>b == p</code>.",
                    "If that count is <code>n - 1</code>, return <code>p</code>.",
                    "If nobody qualifies, return <code>-1</code>.",
                ],
                "why": [
                    "The two checks are exactly the definition of the judge, and pairs are distinct, so n − 1 pairs ending at <code>p</code> means n − 1 different people trust them.",
                    "Each candidate scans the t pairs up to twice: <strong>O(n · t)</strong> time.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "p=1: pair [1, 3] starts at 1, so skip. p=2: [2, 3] starts at 2, skip.",
                        "p=3: no pair starts at 3.",
                        "Pairs ending at 3: [1,3], [2,3], [4,3], so the count is 3 = n − 1.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "p=1: [1, 3] starts at 1, skip. p=2: [2, 3], skip.",
                        "p=3: [3, 1] starts at 3, so 3 trusts someone and is skipped too.",
                        "Nobody is left. The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can there be at most one judge?",
                     "Two judges would each have to trust the other, contradicting \"trusts nobody\"."],
                    ["What about <code>n = 1</code> and no pairs?",
                     "Person 1 trusts nobody and is trusted by 0 = n − 1 people, so 1 is returned, which is correct."],
                    ["Why is this too slow for large inputs?",
                     "With n = 1000 and t up to 10<sup>4</sup>, it does around 10<sup>7</sup> pair checks, versus 10<sup>4</sup> for the degree counts."],
                ],
            },
            "In-degree and out-degree arrays": {
                "idea": [
                    "Treat trust as a directed graph: <code>a → b</code> when a trusts b.",
                    "The judge is the node with out-degree 0 and in-degree n − 1. Count both degrees in one pass.",
                ],
                "steps": [
                    "Create <code>indeg</code> and <code>outdeg</code> arrays of size <code>n + 1</code> (people are 1-based).",
                    "For each pair <code>(a, b)</code>, increment <code>outdeg[a]</code> and <code>indeg[b]</code>.",
                    "Loop <code>p</code> from 1 to <code>n</code>.",
                    "Return the first <code>p</code> with <code>outdeg[p] == 0</code> and <code>indeg[p] == n - 1</code>.",
                    "Otherwise return <code>-1</code>.",
                ],
                "why": [
                    "The degrees encode exactly the two judge conditions, read in O(1) per person.",
                    "One pass over the pairs and one over the people: <strong>O(n + t)</strong> time.",
                    "Two arrays of n + 1: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "outdeg: 1→2, 2→2, 4→1, 3→0.",
                        "indeg: 3→3, 4→2, others 0.",
                        "p=3 has outdeg 0 and indeg 3 = n − 1.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "outdeg: 1→1, 2→1, 3→1.",
                        "indeg: 3→2, 1→1.",
                        "Person 3 has indeg 2 = n − 1 but outdeg 1, so fails. Nobody has outdeg 0.",
                        "The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why size <code>n + 1</code>?",
                     "People are numbered 1..n, so index 0 is simply unused and no shifting is needed."],
                    ["Is checking <code>outdeg[p] == 0</code> really necessary?",
                     "Yes. In the second example person 3 is trusted by everyone else but also trusts person 1, so is not the judge."],
                    ["Could I return as soon as I see the condition?",
                     "Yes, at most one person can satisfy it, so the first match is the only one."],
                ],
            },
            "One net-trust score": {
                "idea": [
                    "Combine both degrees into one number: <code>score = indeg − outdeg</code>.",
                    "Only the judge can reach n − 1: that needs n − 1 incoming trusts (the maximum possible) and no outgoing ones.",
                ],
                "steps": [
                    "Create <code>score</code> of size <code>n + 1</code>.",
                    "For each pair <code>(a, b)</code>: <code>score[a] -= 1</code> and <code>score[b] += 1</code>.",
                    "Loop <code>p</code> from 1 to <code>n</code>.",
                    "Return the first <code>p</code> with <code>score[p] == n - 1</code>.",
                    "Otherwise return <code>-1</code>.",
                ],
                "why": [
                    "Nobody can be trusted by more than n − 1 others, since pairs are distinct and nobody trusts themselves. So a score of n − 1 forces in-degree n − 1 and out-degree 0.",
                    "<strong>O(n + t)</strong> time, like the two-array version.",
                    "One array: <strong>O(n)</strong> space, half of the two-array version.",
                ],
                "dry": [
                    [
                        "[1,3], [1,4]: score[1] = −2, score[3] = 1, score[4] = 1.",
                        "[2,3], [2,4]: score[2] = −2, score[3] = 2, score[4] = 2.",
                        "[4,3]: score[4] = 1, score[3] = 3.",
                        "score[3] = 3 = n − 1. The result is <strong>3</strong>.",
                    ],
                    [
                        "[1,3], [2,3]: score[1] = −1, score[2] = −1, score[3] = 2.",
                        "[3,1]: score[3] = 1, score[1] = 0.",
                        "Nobody reaches n − 1 = 2: person 3 lost one point for trusting 1.",
                        "The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Could someone reach n − 1 without being the judge?",
                     "No. In-degree is at most n − 1, so the score is n − 1 only if in-degree is n − 1 and out-degree is 0."],
                    ["What if the input had duplicate trust pairs?",
                     "Then the argument breaks, since in-degree could exceed n − 1. The problem guarantees pairs are unique."],
                    ["Is one array really better than two?",
                     "Same time complexity; it just halves memory and is a neat interview follow-up."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ number of islands
    "number-of-islands": {
        "examples": [
            {"setup": "g = [list(\"11000\"), list(\"11000\"), list(\"00100\"), list(\"00011\")]",
             "call": "num_islands(g)", "expect": "3"},
            {"setup": "g = [list(\"101\"), list(\"010\"), list(\"101\")]",
             "call": "num_islands(g)", "expect": "5"},
        ],
        "approaches": {
            "Recursive DFS, sinking visited land": {
                "idea": [
                    "Scan the grid; every time you reach land that has not been explored yet, you have found a new island.",
                    "Immediately flood the whole island by turning its cells into water (\"sinking\"), so none of them starts another count.",
                ],
                "steps": [
                    "Copy the grid so the caller's input is not changed.",
                    "<code>sink(r, c)</code>: if <code>(r, c)</code> is inside the grid and is \"1\", set it to \"0\" and call <code>sink</code> on its four neighbours.",
                    "Scan every cell in row-major order.",
                    "On a \"1\", add 1 to <code>count</code> and call <code>sink(r, c)</code>.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "<code>sink</code> reaches exactly the cells 4-connected to the start, so one call removes one whole island, and each island's first scanned cell triggers exactly one count.",
                    "Each cell is sunk at most once and checked from at most 4 neighbours: <strong>O(m · n)</strong> time.",
                    "The grid copy and the recursion depth (up to m · n for a snake-shaped island) give <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "(0,0) is \"1\": count = 1. sink visits (0,0) → (1,0) → (1,1) → (0,1) and sinks all four.",
                        "(0,1), (1,0), (1,1) are now \"0\" and are skipped by the scan.",
                        "(2,2): count = 2, a single cell. (3,3): count = 3, sink also takes (3,4).",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "Land at the four corners and the centre, with no two sharing a side.",
                        "(0,0): count = 1, sink finds no land neighbours. (0,2): count = 2.",
                        "(1,1): count = 3. (2,0): count = 4. (2,2): count = 5.",
                        "Diagonal contact does not join cells. The result is <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why copy the grid first?",
                     "Sinking writes \"0\" into it. Without the copy the caller's grid would be destroyed, and running the function twice would give 0 the second time."],
                    ["Why raise the recursion limit?",
                     "A 300 × 300 all-land grid can recurse 90,000 deep, beyond Python's default limit of 1000. Very deep recursion can still crash the interpreter, which is why the BFS version is safer."],
                    ["Do diagonal neighbours count?",
                     "No, only up, down, left and right, as the second example shows."],
                ],
            },
            "Iterative BFS with a visited set": {
                "idea": [
                    "Same counting idea, but explore each island with a queue instead of recursion.",
                    "A <code>seen</code> set records explored land, so the input grid is never modified.",
                ],
                "steps": [
                    "Scan every cell; when it is \"1\" and not in <code>seen</code>, add 1 to <code>count</code>.",
                    "Mark it seen and start a <code>deque</code> with it.",
                    "Pop <code>(x, y)</code> from the left and look at its four neighbours.",
                    "Any neighbour inside the grid that is \"1\" and unseen is marked and appended.",
                    "When the queue empties the island is fully marked; continue the scan, then return <code>count</code>.",
                ],
                "why": [
                    "BFS reaches every cell connected to the start and nothing else, so each island is counted once, at its first scanned cell.",
                    "Each cell enters the queue at most once: <strong>O(m · n)</strong> time.",
                    "<code>seen</code> and the queue: <strong>O(m · n)</strong> space, with no recursion-depth risk.",
                ],
                "dry": [
                    [
                        "(0,0): count = 1. BFS pops (0,0), (1,0), (0,1), (1,1) and marks them.",
                        "The rest of the first two rows is water or seen.",
                        "(2,2): count = 2, alone. (3,3): count = 3, BFS adds (3,4).",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "(0,0): count = 1; BFS finds no land neighbour.",
                        "(0,2), (1,1), (2,0), (2,2) each start their own BFS of one cell.",
                        "The result is <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why mark a cell when it is added to the queue, not when popped?",
                     "Otherwise the same cell can be added several times by different neighbours before it is popped, wasting time and memory."],
                    ["BFS or DFS: does it matter?",
                     "Not for the count. BFS with an explicit queue avoids Python's recursion limit."],
                    ["Can I sink cells instead of using <code>seen</code>?",
                     "Yes, if you are allowed to modify the input (or copy it). It saves the set but changes the grid."],
                ],
            },
            "Union-find over land cells": {
                "idea": [
                    "Start with every land cell as its own island, then merge each pair of adjacent land cells.",
                    "Every successful merge joins two islands into one, so the count drops by 1.",
                ],
                "steps": [
                    "<code>parent</code> maps each land cell to itself; <code>count = len(parent)</code>.",
                    "<code>find(x)</code> follows parents to the root, halving the path as it goes.",
                    "For each land cell, look only at the neighbours below and to the right.",
                    "If the neighbour is land and <code>find</code> gives different roots, link them and decrease <code>count</code>.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Each successful union merges two different components, so <code>count</code> always equals the number of components; every adjacency is considered once (from its upper or left cell).",
                    "About 2 · m · n union attempts at near-constant amortised cost each: <strong>O(m · n · α)</strong> time.",
                    "<code>parent</code> holds every land cell: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "7 land cells, so count = 7.",
                        "(0,0)–(1,0): union, count 6. (0,0)–(0,1): union, count 5. (0,1)–(1,1): union, count 4.",
                        "(1,0)–(1,1): already the same root, no change.",
                        "(3,3)–(3,4): union, count 3. The result is <strong>3</strong>.",
                    ],
                    [
                        "5 land cells, so count = 5.",
                        "No land cell has land below it or to its right.",
                        "No unions happen. The result is <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why only check down and right?",
                     "Each adjacency is symmetric, so looking from one end is enough. Checking all four would just repeat failed unions."],
                    ["What is <code>parent[x] = parent[parent[x]]</code>?",
                     "Path halving: each step makes a node skip to its grandparent, which keeps trees shallow."],
                    ["When is union-find better than BFS here?",
                     "When land is added over time (Number of Islands II). Each new cell is one union step instead of a fresh traversal."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max area of island
    "max-area-of-island": {
        "examples": [
            {"call": "max_area_of_island([[1, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1]])", "expect": "6"},
            {"call": "max_area_of_island([[0, 0, 0]])", "expect": "0"},
        ],
        "approaches": {
            "Recursive DFS returning the area": {
                "idea": [
                    "The area of an island starting at a cell is 1 plus the areas reachable from its four neighbours.",
                    "Let the recursive call return that number, and return 0 for water, out-of-grid or already-counted cells.",
                    "The answer is the maximum of <code>area(r, c)</code> over all cells.",
                ],
                "steps": [
                    "<code>area(r, c)</code> returns 0 if the cell is outside, water, or in <code>seen</code>.",
                    "Otherwise add it to <code>seen</code> and return <code>1 + </code> the four neighbour calls.",
                    "Call <code>area</code> from every cell.",
                    "Cells of an island already counted return 0 on later calls.",
                    "Return the <code>max</code> of all those results.",
                ],
                "why": [
                    "The first call that reaches an island counts every cell of it once, because <code>seen</code> stops repeats; all later calls into it return 0.",
                    "Each cell is entered once and probed by at most 4 neighbours: <strong>O(m · n)</strong> time.",
                    "<code>seen</code> and recursion depth: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "area(0,0) = 1 + area(1,0) + area(0,1) = 3.",
                        "Calls from (0,1), (1,0) and other water cells return 0.",
                        "area(1,3) floods (1,3), (2,3), (2,2), (3,2), (3,1), (3,3): 6.",
                        "The max over all cells is <strong>6</strong>.",
                    ],
                    [
                        "area(0,0): grid[0][0] == 0, so it returns 0 without touching <code>seen</code>.",
                        "area(0,1) and area(0,2) return 0 for the same reason.",
                        "The max of [0, 0, 0] is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does a grid with no land return 0 and not crash?",
                     "<code>max</code> is taken over every cell's result, never an empty list, and water cells give 0."],
                    ["Why is <code>seen</code> needed if the grid holds 0s and 1s?",
                     "Without it, neighbours would call back into each other forever. Setting the cell to 0 would also work but would modify the input."],
                    ["Why add 1 before the neighbour calls?",
                     "The 1 counts the current cell; each neighbour call returns the size of the not-yet-counted part reachable through it."],
                ],
            },
            "Iterative flood fill with a stack": {
                "idea": [
                    "Same idea without recursion: each unseen land cell starts a stack-based flood fill that counts the cells it pops.",
                    "Keep the largest count seen so far.",
                ],
                "steps": [
                    "Scan every cell; on unseen land, mark it and start <code>stack = [(r, c)]</code> with <code>size = 0</code>.",
                    "Pop a cell and add 1 to <code>size</code>.",
                    "Push each in-grid, land, unseen neighbour after marking it.",
                    "When the stack empties, update <code>best = max(best, size)</code>.",
                    "Return <code>best</code> after the scan.",
                ],
                "why": [
                    "Cells are marked when pushed, so each island cell is popped exactly once and <code>size</code> is the island's area.",
                    "Every cell is pushed at most once: <strong>O(m · n)</strong> time.",
                    "<code>seen</code> and the stack: <strong>O(m · n)</strong> space, without recursion limits.",
                ],
                "dry": [
                    [
                        "(0,0): pops (0,0), (0,1), (1,0): size 3, best = 3.",
                        "(1,3): pops (1,3), (2,3), (2,2), (3,2), (3,1), (3,3): size 6.",
                        "best = max(3, 6) = 6. No more unseen land.",
                        "The result is <strong>6</strong>.",
                    ],
                    [
                        "(0,0), (0,1), (0,2) are all water, so the <code>if</code> fails for each.",
                        "No flood fill starts and <code>best</code> is never updated.",
                        "It keeps its initial value: the result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start <code>best</code> at 0?",
                     "A grid without land has area 0, and every real island is at least 1."],
                    ["Does it matter that it is a stack, not a queue?",
                     "No. Any order visits the same cells; only the area is used."],
                    ["Is <code>size</code> counted on pop or push?",
                     "On pop, once per cell. Counting on push would also work if the start cell is counted too."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ clone graph
    "clone-graph": {
        "examples": [
            {"setup": CLONE_SETUP, "call": "dump(copy)",
             "expect": "[(1, [2, 4], False), (2, [1, 3], False), (3, [2, 4], False), (4, [1, 3], False)]"},
            {"setup": CLONE_SETUP_2, "call": "dump(copy)",
             "expect": "[(1, [2], False), (2, [1], False)]"},
        ],
        "approaches": {
            "DFS with an original &rarr; copy map": {
                "idea": [
                    "Walk the graph and create one new node per original node, wiring each copy to the copies of its neighbours.",
                    "A dictionary <code>copies</code> from original to copy does two jobs: it marks a node as visited and hands back its copy when a cycle returns to it.",
                ],
                "steps": [
                    "<code>clone(n)</code>: if <code>n</code> is in <code>copies</code>, return that copy.",
                    "Otherwise create <code>Node(n.val)</code> and store it in <code>copies[n]</code> <em>before</em> recursing.",
                    "Set its neighbours to <code>[clone(nb) for nb in n.neighbors]</code>, in the original order.",
                    "Return the copy.",
                    "Call <code>clone(node)</code>, or return <code>None</code> for an empty graph.",
                ],
                "why": [
                    "Each original node gets exactly one copy because the map is checked first, and each copy's neighbour list mirrors the original's, so the structure is identical.",
                    "Registering the copy before recursing means a cycle back to it returns the half-built copy instead of recursing forever.",
                    "Each node is copied once and each edge followed once from each end: <strong>O(V + E)</strong> time. The map and recursion take <strong>O(V)</strong> space.",
                ],
                "dry": [
                    [
                        "clone(1) creates c1, then clones neighbour 2: creates c2, whose neighbour 1 is already mapped and returns c1.",
                        "c2 then clones 3: creates c3; 3's neighbour 2 returns c2, and it clones 4.",
                        "c4's neighbours 1 and 3 are both mapped: c4.neighbors = [c1, c3]. Back up: c3 = [c2, c4], c2 = [c1, c3].",
                        "c1's second neighbour 4 is mapped: c1 = [c2, c4]. The dump is <strong>[(1, [2, 4], False), (2, [1, 3], False), (3, [2, 4], False), (4, [1, 3], False)]</strong>.",
                    ],
                    [
                        "clone(1) creates c1 and stores it, then clones 2.",
                        "clone(2) creates c2; its neighbour 1 is already in <code>copies</code>, so c2.neighbors = [c1].",
                        "Back in clone(1): c1.neighbors = [c2]. The cycle 1 ↔ 2 stops at the map.",
                        "The dump is <strong>[(1, [2], False), (2, [1], False)]</strong>.",
                    ],
                ],
                "faq": [
                    ["What happens if the copy is stored after the neighbours are cloned?",
                     "In the second example clone(1) → clone(2) → clone(1) would not find a copy and would recurse forever."],
                    ["Why key the map by node and not by <code>val</code>?",
                     "Keying by node always works. Values are unique in this problem, so a <code>val</code> key would also work here, but not in general."],
                    ["Does the copy keep neighbour order?",
                     "Yes, the list comprehension follows <code>n.neighbors</code> in order."],
                ],
            },
            "BFS with an original &rarr; copy map": {
                "idea": [
                    "The same original → copy map, filled level by level with a queue instead of recursion.",
                    "A node's copy is created the first time it is seen as a neighbour; its neighbour list is filled when it is popped.",
                ],
                "steps": [
                    "Return <code>None</code> for an empty graph; otherwise <code>copies = {node: Node(node.val)}</code> and <code>queue = deque([node])</code>.",
                    "Pop an original <code>n</code>.",
                    "For each neighbour <code>nb</code>: if it has no copy, create one and enqueue <code>nb</code>.",
                    "Append <code>copies[nb]</code> to <code>copies[n].neighbors</code>.",
                    "When the queue is empty, return <code>copies[node]</code>.",
                ],
                "why": [
                    "Every reachable node is enqueued once (when its copy is created) and popped once, so every original edge is appended exactly once to the right copy.",
                    "<strong>O(V + E)</strong> time.",
                    "The map and queue: <strong>O(V)</strong> space, with no recursion depth limit.",
                ],
                "dry": [
                    [
                        "Pop 1: neighbours 2 and 4 are new, so create c2 and c4, enqueue both; c1 = [c2, c4].",
                        "Pop 2: 1 is known, 3 is new, so create c3; c2 = [c1, c3]. Queue: [4, 3].",
                        "Pop 4: c4 = [c1, c3]. Pop 3: c3 = [c2, c4].",
                        "The dump is <strong>[(1, [2, 4], False), (2, [1, 3], False), (3, [2, 4], False), (4, [1, 3], False)]</strong>.",
                    ],
                    [
                        "copies = {1: c1}, queue = [1].",
                        "Pop 1: 2 is new, create c2, enqueue it; c1 = [c2].",
                        "Pop 2: 1 is known; c2 = [c1]. The queue is empty.",
                        "The dump is <strong>[(1, [2], False), (2, [1], False)]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why append the neighbour copy even when it already existed?",
                     "Existing just means the copy was created; the edge from <code>n</code> to it still has to be recorded on <code>copies[n]</code>."],
                    ["Can an edge be appended twice?",
                     "No. Each node is popped once, and each pop handles that node's own neighbour list once."],
                    ["Why use the map as the visited set?",
                     "Having a copy is the same as having been discovered, so a separate set would duplicate it."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ walls and gates
    "walls-and-gates": {
        "examples": [
            {"setup": "INF = 2147483647\nR = [[INF, -1, 0, INF], [INF, INF, INF, -1], [INF, -1, INF, -1], [0, -1, INF, INF]]\nwalls_and_gates(R)",
             "call": "R", "expect": "[[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]"},
            {"setup": "INF = 2147483647\nR = [[INF, -1], [-1, 0]]\nwalls_and_gates(R)",
             "call": "R", "expect": "[[2147483647, -1], [-1, 0]]"},
        ],
        "approaches": {
            "BFS from every empty room": {
                "idea": [
                    "For one room, a BFS outward finds the nearest gate: BFS meets cells in order of distance, so the first gate dequeued is the closest.",
                    "Run that search separately from every empty room.",
                    "Read from a copy <code>original</code> so distances already written do not confuse later searches.",
                ],
                "steps": [
                    "Copy the grid into <code>original</code>.",
                    "For each cell that is <code>INF</code> in <code>original</code>, start a BFS with <code>(r, c, 0)</code> and its own <code>seen</code>.",
                    "Pop <code>(x, y, d)</code>; if <code>original[x][y] == 0</code>, write <code>rooms[r][c] = d</code> and stop this search.",
                    "Otherwise enqueue every in-grid, non-wall, unseen neighbour with distance <code>d + 1</code>.",
                    "If the queue empties without a gate, the room keeps <code>INF</code>.",
                ],
                "why": [
                    "BFS dequeues cells in non-decreasing distance, so the first gate popped is at the shortest path distance from the room.",
                    "Each of the up to m · n rooms runs a BFS over up to m · n cells: <strong>O((m · n)²)</strong> time.",
                    "The copy, one <code>seen</code> set and one queue at a time: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "Room (0,0): BFS pops (0,0), (1,0), (2,0), (1,1) and then the gate (3,0) at d = 3. Five pops.",
                        "Room (0,3): pops itself, then the gate (0,2) at d = 1. Room (1,2): the gate (0,2) at d = 1.",
                        "Rooms (1,0), (1,1), (2,2) get 2; (2,0) gets 1; (3,2) gets 3.",
                        "Room (3,3): five pops to reach (0,2) at d = 4. The grid becomes <strong>[[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]</strong>.",
                    ],
                    [
                        "Only (0,0) is an empty room.",
                        "Its BFS pops (0,0); both neighbours (1,0) and (0,1) are walls, so nothing is enqueued.",
                        "The queue empties without a gate, and the room stays INF.",
                        "The grid is unchanged: <strong>[[2147483647, -1], [-1, 0]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why read from <code>original</code> and not <code>rooms</code>?",
                     "Rooms already filled hold small numbers. They are not gates, but reading them is confusing and the gate test must look at the true grid; the copy keeps the input semantics fixed."],
                    ["Why <code>break</code> at the first gate?",
                     "BFS order guarantees no later gate can be closer, so the rest of the search is wasted."],
                    ["Why is this too slow?",
                     "Every room repeats almost the same search. Starting from all gates at once does the whole grid in one pass."],
                ],
            },
            "Multi-source BFS from all gates at once": {
                "idea": [
                    "Turn the question around: spread outward from every gate simultaneously.",
                    "Put all gates in the queue at distance 0. BFS then reaches each room first from its nearest gate.",
                    "The first time a room is reached, its distance is final, so <code>rooms[a][b] == INF</code> doubles as the visited check.",
                ],
                "steps": [
                    "Start <code>queue</code> with every cell whose value is 0.",
                    "Pop <code>(r, c)</code> and look at its four neighbours <code>(a, b)</code>.",
                    "If a neighbour is in the grid and still <code>INF</code>, set it to <code>rooms[r][c] + 1</code>.",
                    "Append that neighbour to the queue.",
                    "Walls (−1), gates (0) and already-filled rooms are never changed. Unreachable rooms stay <code>INF</code>.",
                ],
                "why": [
                    "With several sources, BFS still pops cells in non-decreasing distance from the nearest source, so the first write to a room is its shortest distance to any gate.",
                    "Each cell is written and enqueued at most once: <strong>O(m · n)</strong> time.",
                    "The queue can hold O(m · n) cells: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "queue = [(0,2), (3,0)], the two gates.",
                        "Pop (0,2): (1,2) = 1, (0,3) = 1. Pop (3,0): (2,0) = 1.",
                        "Pop (1,2): (2,2) = 2, (1,1) = 2. Pop (2,0): (1,0) = 2.",
                        "Pop (2,2): (3,2) = 3. Pop (1,0): (0,0) = 3. Pop (3,2): (3,3) = 4.",
                        "The grid becomes <strong>[[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]</strong>.",
                    ],
                    [
                        "queue = [(1,1)], the only gate.",
                        "Pop (1,1): its neighbours (0,1) and (1,0) are walls (−1), so neither is INF.",
                        "The queue empties; (0,0) is never reached.",
                        "The grid is unchanged: <strong>[[2147483647, -1], [-1, 0]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the first visit already the shortest distance?",
                     "All gates start at distance 0, and the queue processes all distance-d cells before any distance-(d + 1) cell, so no shorter route can arrive later."],
                    ["Why check <code>rooms[a][b] == INF</code> instead of keeping a <code>seen</code> set?",
                     "A room is INF exactly when it has not been reached. Walls and gates are never INF, so they are skipped automatically."],
                    ["Would DFS from each gate work?",
                     "Only with re-relaxing distances when a shorter one is found, which can revisit cells many times. BFS gets it right in one visit."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ rotting oranges
    "rotting-oranges": {
        "examples": [
            {"call": "oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]])", "expect": "4"},
            {"call": "oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]])", "expect": "-1"},
        ],
        "approaches": {
            "Simulate minute by minute": {
                "idea": [
                    "Play the process literally: each minute, every fresh orange touching a rotten one turns rotten.",
                    "Collect all such oranges first, then rot them together, so a newly rotten orange does not spread in the same minute.",
                    "Stop when a minute changes nothing; any fresh orange left is unreachable.",
                ],
                "steps": [
                    "Copy the grid into <code>g</code>.",
                    "Build <code>rot</code>: every cell equal to 1 with a neighbour equal to 2.",
                    "If <code>rot</code> is empty, stop.",
                    "Otherwise set those cells to 2 and add 1 to <code>minutes</code>; repeat.",
                    "Return <code>-1</code> if any 1 remains, else <code>minutes</code>.",
                ],
                "why": [
                    "Building the whole <code>rot</code> list before changing anything matches the rule that rot spreads one step per minute.",
                    "Each minute scans all m · n cells, and there can be up to m · n minutes (a long snake): <strong>O((m · n)²)</strong> time.",
                    "The copy and the list: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "Minute 1: rot = [(0,1), (1,0)].",
                        "Minute 2: rot = [(0,2), (1,1)]. Minute 3: rot = [(2,1)].",
                        "Minute 4: rot = [(2,2)]. Then rot is empty and no 1 remains.",
                        "The result is <strong>4</strong>.",
                    ],
                    [
                        "Minute 1: (0,1). Minute 2: (0,2), (1,1). Minute 3: (1,2). Minute 4: (2,2).",
                        "Next scan: rot is empty.",
                        "(2,0) is still fresh: both of its neighbours, (1,0) and (2,1), are empty cells, so rot can never reach it.",
                        "The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not rot cells as you find them during the scan?",
                     "A cell rotted early in the scan would infect cells later in the same scan, so rot would travel several steps in one minute."],
                    ["What if there are no fresh oranges at all?",
                     "The first scan finds nothing, <code>minutes</code> stays 0, and 0 is returned."],
                    ["Why is this the slow version?",
                     "Every minute rescans the whole grid even though only the rot front changes. BFS only looks at the front."],
                ],
            },
            "Multi-source BFS by levels": {
                "idea": [
                    "All initially rotten oranges spread at the same time, so start a BFS from all of them at once.",
                    "Each BFS level is one minute; the queue always holds exactly the oranges that turned rotten in the last minute.",
                    "Count fresh oranges up front so the end check is just <code>fresh == 0</code>.",
                ],
                "steps": [
                    "Copy the grid; put every 2 in <code>queue</code> and count the 1s in <code>fresh</code>.",
                    "While the queue is non-empty and <code>fresh</code> is positive, process exactly <code>len(queue)</code> cells: one minute.",
                    "For each, rot every fresh neighbour: set it to 2, decrease <code>fresh</code>, enqueue it.",
                    "After the level, add 1 to <code>minutes</code>.",
                    "Return <code>-1</code> if <code>fresh</code> is still positive, else <code>minutes</code>.",
                ],
                "why": [
                    "Level-by-level BFS from all sources rots each orange at its shortest distance to any initially rotten orange, which is exactly the minute it rots.",
                    "Each cell is enqueued at most once: <strong>O(m · n)</strong> time.",
                    "The queue and the copy: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "queue = [(0,0)], fresh = 6.",
                        "Minute 1: rot (1,0), (0,1); fresh = 4. Minute 2: rot (1,1), (0,2); fresh = 2.",
                        "Minute 3: rot (2,1); fresh = 1. Minute 4: rot (2,2); fresh = 0.",
                        "The loop stops on fresh = 0. The result is <strong>4</strong>.",
                    ],
                    [
                        "queue = [(0,0)], fresh = 6.",
                        "Minutes 1–4 rot (0,1), then (1,1) and (0,2), then (1,2), then (2,2); fresh = 1.",
                        "Minute 5 pops (2,2) but rots nothing; the queue is now empty.",
                        "fresh = 1, from the cut-off (2,0). The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the loop also test <code>fresh</code>?",
                     "Without it, the last level (which rots nothing) would still add a minute, giving 5 instead of 4 in the first example."],
                    ["Why <code>for _ in range(len(queue))</code>?",
                     "<code>len(queue)</code> is fixed when the range is created, so only the cells from this minute are processed; cells added now belong to the next minute."],
                    ["What if there are no fresh oranges?",
                     "The loop never runs and 0 is returned, even when there are no rotten ones either."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ pacific atlantic water flow
    "pacific-atlantic": {
        "examples": [
            {"call": "sorted(pacific_atlantic([[1, 2, 3], [8, 9, 4], [7, 6, 5]]))",
             "expect": "[[0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]"},
            {"call": "sorted(pacific_atlantic([[3, 3, 3], [3, 1, 3], [3, 3, 3]]))",
             "expect": "[[0, 0], [0, 1], [0, 2], [1, 0], [1, 2], [2, 0], [2, 1], [2, 2]]"},
        ],
        "approaches": {
            "DFS from every cell": {
                "idea": [
                    "Water moves from a cell to a neighbour of equal or lower height. Follow every such path from each cell.",
                    "Record whether any reached cell touches the Pacific (top or left edge) and the Atlantic (bottom or right edge).",
                ],
                "steps": [
                    "For each cell <code>(r, c)</code>, start a DFS with its own <code>seen</code> and <code>stack</code>.",
                    "Pop <code>(x, y)</code>; set <code>pac</code> if <code>x == 0 or y == 0</code> and <code>atl</code> if <code>x == m - 1 or y == n - 1</code>.",
                    "Push each in-grid, unseen neighbour with height ≤ <code>heights[x][y]</code>.",
                    "Stop early once both flags are true.",
                    "If both are true, append <code>[r, c]</code> to <code>out</code>.",
                ],
                "why": [
                    "The DFS finds exactly the cells water can reach from <code>(r, c)</code>, and a reached border cell drains into its ocean.",
                    "Up to m · n searches of up to m · n cells: <strong>O((m · n)²)</strong> time.",
                    "One <code>seen</code> set and stack at a time: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "(0,0) height 1: no lower neighbour, only Pacific. (0,1): reaches (0,0), still only Pacific.",
                        "(0,2): on the top and right edges, both oceans at once. (1,0): reaches (2,0) at the bottom, both.",
                        "(1,1) height 9 pops (1,0), (0,0), (2,0): both. (1,2), (2,0), (2,1), (2,2) all reach both too.",
                        "The result is <strong>[[0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]</strong>.",
                    ],
                    [
                        "Every border cell has height 3 and sits on an edge; equal heights let water slide along the border to the other ocean, so all reach both.",
                        "(1,1) has height 1 and every neighbour is 3, so water cannot leave it: neither flag is set.",
                        "The centre is the only cell left out.",
                        "The result is <strong>[[0, 0], [0, 1], [0, 2], [1, 0], [1, 2], [2, 0], [2, 1], [2, 2]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;=</code> and not <code>&lt;</code>?",
                     "Water can flow onto a neighbour of equal height. In the second example the border cells rely on that to reach the far ocean."],
                    ["Why is a fresh <code>seen</code> needed for every cell?",
                     "Reachability depends on the start, so one search's visited cells say nothing about the next one."],
                    ["Can results from one search be reused?",
                     "Not easily, since a search may stop early. Reversing the direction of the search is the clean way to share work."],
                ],
            },
            "Reverse flow: search uphill from each ocean": {
                "idea": [
                    "Instead of asking where water from each cell can go, ask which cells can drain into each ocean.",
                    "Start from all cells on an ocean's edges and climb to neighbours of equal or greater height: water could flow back down that way.",
                    "The answer is the intersection of the two reachable sets.",
                ],
                "steps": [
                    "<code>reach(starts)</code> does one DFS from all start cells at once with a shared <code>seen</code>.",
                    "It pushes a neighbour when it is in-grid, unseen and <code>heights[a][b] &gt;= heights[x][y]</code>.",
                    "Run it from the top row and left column for <code>pacific</code>.",
                    "Run it from the bottom row and right column for <code>atlantic</code>.",
                    "Return the cells in <code>pacific &amp; atlantic</code>, sorted.",
                ],
                "why": [
                    "A cell is reached by the uphill search exactly when there is a non-increasing path from it down to that ocean's edge.",
                    "Each search visits every cell at most once: two searches, <strong>O(m · n)</strong> time.",
                    "Two sets and a stack: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pacific starts: (0,0), (0,1), (0,2), (1,0), (2,0).",
                        "Climbs (1,0)→(1,1), (0,2)→(1,2)→(2,2)→(2,1): pacific has all 9 cells.",
                        "Atlantic starts: bottom row and right column. Climbs (1,2)→(1,1) and (2,0)→(1,0): (0,0) and (0,1) are never reached.",
                        "The intersection is <strong>[[0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]</strong>.",
                    ],
                    [
                        "Pacific starts: the top row and left column, all height 3.",
                        "The only unvisited cell is the centre, height 1, which is lower than 3: no climb. Pacific = 8 border cells.",
                        "Atlantic is the same 8 cells for the same reason.",
                        "The intersection is <strong>[[0, 0], [0, 1], [0, 2], [1, 0], [1, 2], [2, 0], [2, 1], [2, 2]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&gt;=</code> in the reverse search?",
                     "We walk against the flow. Water goes from high to low (or equal), so the reverse step goes from low to high (or equal)."],
                    ["Why start all edge cells in one search?",
                     "One shared <code>seen</code> means each cell is processed once per ocean, which is what makes it linear."],
                    ["Does a corner cell like (0, n − 1) count for both oceans?",
                     "Yes, it is on the top edge and the right edge, so it is a start cell of both searches."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ surrounded regions
    "surrounded-regions": {
        "examples": [
            {"setup": "B = [list(\"XXXX\"), list(\"XOOX\"), list(\"XXOX\"), list(\"XOXX\")]\nsolve(B)",
             "call": "B", "expect": "[[\"X\", \"X\", \"X\", \"X\"], [\"X\", \"X\", \"X\", \"X\"], [\"X\", \"X\", \"X\", \"X\"], [\"X\", \"O\", \"X\", \"X\"]]"},
            {"setup": "B = [list(\"XXXX\"), list(\"XOOX\"), list(\"XXOX\"), list(\"XXOX\")]\nsolve(B)",
             "call": "B", "expect": "[[\"X\", \"X\", \"X\", \"X\"], [\"X\", \"O\", \"O\", \"X\"], [\"X\", \"X\", \"O\", \"X\"], [\"X\", \"X\", \"O\", \"X\"]]"},
        ],
        "approaches": {
            "Explore each region, flip if it never touches the border": {
                "idea": [
                    "Group the \"O\" cells into connected regions.",
                    "A region is captured exactly when none of its cells lies on the border, so explore it fully, remember whether it touched the border, then decide.",
                ],
                "steps": [
                    "Scan cells; an unseen \"O\" starts a new region with <code>region = []</code>, <code>border = False</code>.",
                    "Pop cells off <code>stack</code>, append them to <code>region</code>, and set <code>border</code> if the cell is in the first or last row or column.",
                    "Push in-grid, unseen \"O\" neighbours.",
                    "When the region is complete and <code>border</code> is false, set all its cells to \"X\".",
                    "Continue the scan; <code>seen</code> stops a region being explored twice.",
                ],
                "why": [
                    "The region is collected completely before flipping, so one border cell anywhere in it saves all of it.",
                    "Each cell is pushed once and flipped at most once: <strong>O(m · n)</strong> time.",
                    "<code>seen</code>, <code>region</code> and the stack: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "(1,1) starts a region: it collects (1,1), (1,2), (2,2). None is on the border.",
                        "border = False, so the three cells become \"X\".",
                        "(3,1) starts a region of one cell in the last row: border = True, kept.",
                        "The board is <strong>[[\"X\", \"X\", \"X\", \"X\"], [\"X\", \"X\", \"X\", \"X\"], [\"X\", \"X\", \"X\", \"X\"], [\"X\", \"O\", \"X\", \"X\"]]</strong>.",
                    ],
                    [
                        "(1,1) starts a region: (1,1), (1,2), (2,2), (3,2).",
                        "(3,2) is in the last row, so border = True.",
                        "The whole region survives, even though three of its cells are inside.",
                        "The board is unchanged: <strong>[[\"X\", \"X\", \"X\", \"X\"], [\"X\", \"O\", \"O\", \"X\"], [\"X\", \"X\", \"O\", \"X\"], [\"X\", \"X\", \"O\", \"X\"]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not flip cells while exploring?",
                     "You do not know whether the region touches the border until it is fully explored, as the second example shows."],
                    ["Why does the second example keep (1,1), which is far from the edge?",
                     "It is connected through (1,2) and (2,2) to (3,2) on the border, and the rule is about the whole region."],
                    ["Is <code>seen</code> needed for regions that are flipped?",
                     "Flipped cells become \"X\" and would be skipped anyway, but kept regions remain \"O\", so <code>seen</code> stops them being explored again."],
                ],
            },
            "Mark safe cells from the border, then flip": {
                "idea": [
                    "Turn it around: an \"O\" survives exactly when it is connected to an \"O\" on the border.",
                    "Flood from every border \"O\" and mark what you reach as safe (\"S\"); every \"O\" left unmarked is captured.",
                ],
                "steps": [
                    "Put every border cell holding \"O\" on <code>stack</code>.",
                    "Pop <code>(r, c)</code>; if it is in the grid and still \"O\", mark it \"S\" and push its four neighbours.",
                    "When the stack is empty, all border-connected cells are \"S\".",
                    "Rewrite every cell: \"S\" becomes \"O\", everything else becomes \"X\".",
                ],
                "why": [
                    "The flood reaches exactly the \"O\" cells connected to the border, which are exactly the ones that must stay.",
                    "Each cell turns to \"S\" at most once and pushes 4 neighbours then: <strong>O(m · n)</strong> time.",
                    "Neighbours are pushed before they are checked, so the stack can hold several entries per cell: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "Border \"O\" cells: only (3,1). stack = [(3,1)].",
                        "Pop (3,1): mark it \"S\" and push its neighbours; they are all \"X\" or off the grid.",
                        "Final pass: (3,1) goes back to \"O\"; (1,1), (1,2), (2,2) are plain \"O\" and become \"X\".",
                        "The board is <strong>[[\"X\", \"X\", \"X\", \"X\"], [\"X\", \"X\", \"X\", \"X\"], [\"X\", \"X\", \"X\", \"X\"], [\"X\", \"O\", \"X\", \"X\"]]</strong>.",
                    ],
                    [
                        "Border \"O\" cells: only (3,2).",
                        "The flood marks (3,2), then (2,2), then (1,2), then (1,1) as \"S\".",
                        "Final pass: all four return to \"O\"; nothing else was \"O\".",
                        "The board is unchanged: <strong>[[\"X\", \"X\", \"X\", \"X\"], [\"X\", \"O\", \"O\", \"X\"], [\"X\", \"X\", \"O\", \"X\"], [\"X\", \"X\", \"O\", \"X\"]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why use a temporary \"S\" instead of a <code>seen</code> set?",
                     "Marking on the board is the visited check and saves the set. The final pass turns it back into \"O\"."],
                    ["Why push neighbours without checking them first?",
                     "It keeps the code short: the check happens on pop. The cost is more stack entries, which is why the space is listed as a worst-case stack."],
                    ["Why is this usually preferred?",
                     "It only explores border-connected regions and needs no per-region bookkeeping."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ open the lock
    "open-the-lock": {
        "examples": [
            {"call": "open_lock([\"8888\"], \"0009\")", "expect": "1"},
            {"call": "open_lock([\"0201\", \"0101\", \"0102\", \"1212\", \"2002\"], \"0202\")", "expect": "6"},
        ],
        "approaches": {
            "BFS from the start": {
                "idea": [
                    "Each lock state is a node; one move turns one wheel by one step up or down, so each state has 8 neighbours.",
                    "The fewest moves is the shortest path in an unweighted graph, which BFS finds.",
                    "Deadends are simply nodes you may not enter.",
                ],
                "steps": [
                    "Put deadends in a set <code>dead</code>; if \"0000\" is dead, return -1.",
                    "Start <code>queue</code> with <code>(\"0000\", 0)</code> and <code>seen = {\"0000\"}</code>.",
                    "Pop <code>(state, moves)</code>; if it equals <code>target</code>, return <code>moves</code>.",
                    "For each wheel <code>i</code> and direction, build <code>nxt</code> with <code>(d ± 1) % 10</code>.",
                    "Enqueue <code>nxt</code> with <code>moves + 1</code> if it is neither seen nor dead.",
                    "If the queue empties, the target is unreachable: return -1.",
                ],
                "why": [
                    "BFS pops states in order of move count, so the first time the target is popped, its count is minimal.",
                    "There are 10<sup>4</sup> states with 8 neighbours each: <strong>O(10<sup>4</sup> · 8)</strong> time.",
                    "<code>seen</code> and the queue: <strong>O(10<sup>4</sup>)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop \"0000\": enqueue 1000, 9000, 0100, 0900, 0010, 0090, 0001, 0009 with moves 1.",
                        "The wrap-around <code>(0 - 1) % 10 = 9</code> makes 0009 a single move.",
                        "Pops 1000 … 0001 are not the target and enqueue their own moves-2 neighbours.",
                        "The 9th pop is 0009. The result is <strong>1</strong>.",
                    ],
                    [
                        "The direct routes from 0000 to 0202 run into deadends such as 0201, 0102 and 0101.",
                        "BFS keeps expanding level by level around them; 1506 states have been seen by the time the target comes off the queue.",
                        "0202 is first popped at moves 6, e.g. 0000 → 1000 → 1100 → 1200 → 1201 → 1202 → 0202.",
                        "The result is <strong>6</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check the target on pop, not when enqueuing?",
                     "Both are correct for unit-weight BFS. Checking on pop also handles target == \"0000\" without a special case."],
                    ["Why is <code>(d - 1) % 10</code> correct for 0?",
                     "Python's <code>%</code> returns a non-negative result, so <code>-1 % 10 = 9</code>, which is the wrap-around."],
                    ["Why mark seen on enqueue?",
                     "A state reachable from several neighbours would otherwise be enqueued several times, multiplying the work."],
                ],
            },
            "Bidirectional BFS": {
                "idea": [
                    "Search from both the start and the target and stop when the two frontiers meet.",
                    "Two searches of depth d/2 explore far fewer states than one of depth d, because the frontier grows quickly with depth.",
                    "Always expand the smaller frontier to keep the work balanced.",
                ],
                "steps": [
                    "Return -1 if \"0000\" or the target is dead; return 0 if the target is \"0000\".",
                    "Set <code>front = {\"0000\"}</code>, <code>back = {target}</code>, <code>seen</code> = both, <code>moves = 0</code>.",
                    "Each round, swap so <code>front</code> is the smaller set, then add 1 to <code>moves</code>.",
                    "Generate every neighbour of every state in <code>front</code>; if one is in <code>back</code>, return <code>moves</code>.",
                    "Otherwise collect unseen, non-dead neighbours into <code>nxt_front</code>, which becomes <code>front</code>.",
                    "If either frontier empties, return -1.",
                ],
                "why": [
                    "Each frontier is a BFS level from its end; the first round in which a neighbour of one lies in the other gives the shortest total path length.",
                    "With branching factor b and distance d, each side explores about b<sup>d/2</sup> states: <strong>O(b<sup>d/2</sup>)</strong> time in practice, still bounded by 10<sup>4</sup> · 8.",
                    "The frontiers and <code>seen</code>: <strong>O(b<sup>d/2</sup>)</strong> space.",
                ],
                "dry": [
                    [
                        "front = {0000}, back = {0009}. Round 1: moves = 1.",
                        "Expanding 0000 generates 1000, 9000, …, and then 0009, which is in back.",
                        "They meet at once, one move apart.",
                        "The result is <strong>1</strong>.",
                    ],
                    [
                        "Round 1 expands {0000} into 8 states. Round 2 swaps and expands {0202} into 6 (its neighbours 0201 and 0102 are dead).",
                        "Rounds 3–5 keep expanding the smaller side: frontier sizes 28, 31, then 84.",
                        "In round 6, expanding 1100 produces 1200, which is in the other frontier.",
                        "The result is <strong>6</strong>, after seeing far fewer states than the 1506 of the one-sided BFS.",
                    ],
                ],
                "faq": [
                    ["Why is the target checked against <code>back</code> before the dead check?",
                     "States in <code>back</code> were already accepted as non-dead when they were added, so a match is always a valid meeting point."],
                    ["Why swap to expand the smaller set?",
                     "Expansion cost is proportional to the frontier size. Growing the smaller side keeps both near b<sup>d/2</sup>."],
                    ["Is the speedup guaranteed here?",
                     "The state space is only 10<sup>4</sup>, so both are fast; the gain matters for huge implicit graphs like word ladders."],
                ],
            },
        },
    },
}
