# -*- coding: utf-8 -*-
"""Graphs topic, part 1: grids, traversal, topological sort (NeetCode 250:
Graphs). The union-find-shaped Graphs problems (261, 323, 684, 721) live in
the Union Find topic. Assembled into GRAPHS_TOPIC by content/graphs.py."""

SECTION_TRAVERSAL = dict(
    id="traversal",
    title="Grids, BFS and DFS",
    idea=[
        "A grid is a graph whose edges are implicit: each cell's neighbours are the four cells around it. DFS floods a region; BFS explores in rings, so it finds shortest paths in unweighted graphs, and <strong>multi-source BFS</strong> (start with every source in the queue at once) gives each cell its distance to the <em>nearest</em> source in a single pass.",
    ],
    problems=[

    # ------------------------------------------------------------------ 463
    dict(
        id="island-perimeter",
        lc=463, slug="island-perimeter",
        name="Island Perimeter",
        difficulty="easy",
        framing=[
            "A grid holds exactly one island (land cells connected horizontally/vertically, no lakes). Return its perimeter. Every land cell contributes 4 edges, minus one for each side it shares with another land cell.",
        ],
        approaches=[
            dict(
                name="DFS, counting edges that face water or the border",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                why=[
                    "Flood the island from any land cell; every step from land into water or off the grid crosses one unit of perimeter. It is overkill for this problem (the island is guaranteed single), but it is the version that generalises to \"perimeter of the island containing cell X\".",
                ],
                code='''def island_perimeter(grid):
    m, n = len(grid), len(grid[0])
    start = next((r, c) for r in range(m) for c in range(n) if grid[r][c])
    seen, stack, perimeter = {start}, [start], 0
    while stack:
        r, c = stack.pop()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if not (0 <= nr < m and 0 <= nc < n) or grid[nr][nc] == 0:
                perimeter += 1                   # an edge facing water
            elif (nr, nc) not in seen:
                seen.add((nr, nc))
                stack.append((nr, nc))
    return perimeter''',
            ),
            dict(
                name="Count lands and shared edges",
                time="O(m &middot; n)",
                space="O(1)",
                best=True,
                why=[
                    "Perimeter = 4 &times; (land cells) &minus; 2 &times; (adjacent land pairs): each shared edge removes one unit from both cells. Counting only the right and down neighbour of each land cell counts every adjacent pair exactly once. No traversal, no visited set.",
                ],
                code='''def island_perimeter(grid):
    lands = shared = 0
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v:
                lands += 1
                if r + 1 < len(grid) and grid[r + 1][c]:
                    shared += 1
                if c + 1 < len(row) and row[c + 1]:
                    shared += 1
    return 4 * lands - 2 * shared''',
            ),
        ],
        tests='''assert island_perimeter([[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [1, 1, 0, 0]]) == 16
assert island_perimeter([[1]]) == 4 and island_perimeter([[1, 0]]) == 4 and island_perimeter([[1, 1]]) == 6''',
    ),

    # ------------------------------------------------------------------ 953
    dict(
        id="verify-alien-dictionary",
        lc=953, slug="verifying-an-alien-dictionary",
        name="Verifying An Alien Dictionary",
        difficulty="easy",
        framing=[
            "Given an alien alphabet order, are the words sorted? Sorted order only has to hold between <em>adjacent</em> words (it is transitive), and two words are compared at their first differing letter &mdash; or, if one is a prefix of the other, the shorter comes first.",
        ],
        approaches=[
            dict(
                name="Translate to English letters, compare with sorted",
                time="O(C log n)",
                space="O(C)",
                why=[
                    "Map each alien letter to the English letter at the same rank, translate every word, and check the translated list equals its sorted version. Python's string comparison then handles the prefix rule automatically. C is the total number of characters.",
                ],
                code='''def is_alien_sorted(words, order):
    to_english = {ch: chr(97 + i) for i, ch in enumerate(order)}
    translated = ["".join(to_english[ch] for ch in w) for w in words]
    return translated == sorted(translated)''',
            ),
            dict(
                name="Rank map, compare adjacent pairs",
                time="O(C)",
                space="O(1)",
                best=True,
                why=[
                    "Compare each word with the next at the first differing letter using the alphabet's rank. If no letter differs, the pair is only out of order when the first word is longer (\"apple\" before \"app\" is wrong). Linear in the total characters, no sorting, and it stops at the first violation.",
                ],
                code='''def is_alien_sorted(words, order):
    rank = {ch: i for i, ch in enumerate(order)}
    for a, b in zip(words, words[1:]):
        for x, y in zip(a, b):
            if x != y:
                if rank[x] > rank[y]:
                    return False
                break
        else:
            if len(a) > len(b):                  # b is a proper prefix of a
                return False
    return True''',
            ),
        ],
        tests='''assert is_alien_sorted(["hello", "leetcode"], "hlabcdefgijkmnopqrstuvwxyz") is True
assert is_alien_sorted(["word", "world", "row"], "worldabcefghijkmnpqstuvxyz") is False
assert is_alien_sorted(["apple", "app"], "abcdefghijklmnopqrstuvwxyz") is False''',
    ),

    # ------------------------------------------------------------------ 997
    dict(
        id="find-town-judge",
        lc=997, slug="find-the-town-judge",
        name="Find the Town Judge",
        difficulty="easy",
        framing=[
            "The judge trusts nobody and is trusted by everyone else. In graph terms: out-degree 0 and in-degree n - 1. Degrees are all you need.",
        ],
        approaches=[
            dict(
                name="Check each candidate against all trust pairs",
                time="O(n &middot; t)",
                space="O(1)",
                tag="brute force",
                why=["For each person, scan the trust list to see whether they trust anyone and how many trust them."],
                code='''def find_judge(n, trust):
    for p in range(1, n + 1):
        if any(a == p for a, _ in trust):
            continue
        if sum(1 for a, b in trust if b == p) == n - 1:
            return p
    return -1''',
            ),
            dict(
                name="In-degree and out-degree arrays",
                time="O(n + t)",
                space="O(n)",
                why=["One pass over the trust pairs fills both degree arrays; a second finds the person with out 0 and in n - 1."],
                code='''def find_judge(n, trust):
    indeg, outdeg = [0] * (n + 1), [0] * (n + 1)
    for a, b in trust:
        outdeg[a] += 1
        indeg[b] += 1
    for p in range(1, n + 1):
        if outdeg[p] == 0 and indeg[p] == n - 1:
            return p
    return -1''',
            ),
            dict(
                name="One net-trust score",
                time="O(n + t)",
                space="O(n)",
                best=True,
                why=[
                    "Combine the two arrays into one score: +1 for being trusted, -1 for trusting. Only the judge can reach n - 1: that needs n - 1 incoming trusts and zero outgoing (each outgoing would subtract one, and nobody can be trusted more than n - 1 times).",
                ],
                code='''def find_judge(n, trust):
    score = [0] * (n + 1)
    for a, b in trust:
        score[a] -= 1
        score[b] += 1
    for p in range(1, n + 1):
        if score[p] == n - 1:
            return p
    return -1''',
            ),
        ],
        tests='''assert find_judge(2, [[1, 2]]) == 2 and find_judge(3, [[1, 3], [2, 3]]) == 3
assert find_judge(3, [[1, 3], [2, 3], [3, 1]]) == -1 and find_judge(1, []) == 1''',
    ),

    # ------------------------------------------------------------------ 200
    dict(
        id="number-of-islands",
        lc=200, slug="number-of-islands",
        name="Number of Islands",
        difficulty="medium",
        framing=[
            "Count the islands in a grid of '1' (land) and '0' (water). Each unvisited land cell found by a scan starts a new island; flood it so none of its cells is counted again. DFS, BFS and union-find all work &mdash; the differences are in stack depth and in whether the grid is modified.",
        ],
        approaches=[
            dict(
                name="Recursive DFS, sinking visited land",
                time="O(m &middot; n)",
                space="O(m &middot; n) recursion",
                why=[
                    "On finding land, count it and recursively turn its whole island to water. Short and clear, but a 300 &times; 300 grid of land recurses 90,000 deep &mdash; past CPython's default limit. It also destroys the input.",
                ],
                code='''def num_islands(grid):
    import sys
    sys.setrecursionlimit(10 ** 6)
    grid = [row[:] for row in grid]
    m, n = len(grid), len(grid[0])

    def sink(r, c):
        if 0 <= r < m and 0 <= c < n and grid[r][c] == "1":
            grid[r][c] = "0"
            sink(r + 1, c); sink(r - 1, c); sink(r, c + 1); sink(r, c - 1)

    count = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)
    return count''',
            ),
            dict(
                name="Iterative BFS with a visited set",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                best=True,
                why=[
                    "Same scan, but flood each island with a queue, marking cells in a visited set when they are enqueued (not when dequeued, or a cell can be enqueued many times). No recursion limit, and the input grid is left untouched.",
                ],
                code='''def num_islands(grid):
    m, n = len(grid), len(grid[0])
    seen, count = set(), 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] == "1" and (r, c) not in seen:
                count += 1
                seen.add((r, c))
                queue = deque([(r, c)])
                while queue:
                    x, y = queue.popleft()
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == "1" and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            queue.append((nx, ny))
    return count''',
            ),
            dict(
                name="Union-find over land cells",
                time="O(m &middot; n &middot; &alpha;)",
                space="O(m &middot; n)",
                why=[
                    "Start with one set per land cell and union each land cell with its land neighbours to the right and below. The number of successful unions subtracted from the land count is the number of islands. This is the version that extends to Number of Islands II, where land is added cell by cell and the count is needed after each addition.",
                ],
                code='''def num_islands(grid):
    m, n = len(grid), len(grid[0])
    parent = {(r, c): (r, c) for r in range(m) for c in range(n) if grid[r][c] == "1"}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    count = len(parent)
    for (r, c) in list(parent):
        for nb in ((r + 1, c), (r, c + 1)):
            if nb in parent:
                a, b = find((r, c)), find(nb)
                if a != b:
                    parent[a] = b
                    count -= 1
    return count''',
            ),
        ],
        tests='''g1 = [list("11110"), list("11010"), list("11000"), list("00000")]
g2 = [list("11000"), list("11000"), list("00100"), list("00011")]
assert num_islands(g1) == 1 and num_islands(g2) == 3
rng = random.Random(0)
for _ in range(40):
    m, n = rng.randint(1, 7), rng.randint(1, 7)
    g = [[rng.choice("01") for _ in range(n)] for _ in range(m)]
    lab, k = {}, 0
    for r in range(m):
        for c in range(n):
            if g[r][c] == "1" and (r, c) not in lab:
                k += 1; st = [(r, c)]; lab[(r, c)] = k
                while st:
                    x, y = st.pop()
                    for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= a < m and 0 <= b < n and g[a][b] == "1" and (a, b) not in lab:
                            lab[(a, b)] = k; st.append((a, b))
    assert num_islands(g) == k''',
    ),

    # ------------------------------------------------------------------ 695
    dict(
        id="max-area-of-island",
        lc=695, slug="max-area-of-island",
        name="Max Area of Island",
        difficulty="medium",
        framing=[
            "The area of the largest island (number of cells). Number of Islands where each flood fill returns its size instead of just being counted.",
        ],
        approaches=[
            dict(
                name="Recursive DFS returning the area",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                why=[
                    "<code>area(r, c)</code> is 1 plus the areas of its four neighbours, and 0 for water or visited cells. Marking a cell visited before recursing prevents counting it twice. Recursion depth can reach m &middot; n.",
                ],
                code='''def max_area_of_island(grid):
    import sys
    sys.setrecursionlimit(10 ** 6)
    m, n = len(grid), len(grid[0])
    seen = set()

    def area(r, c):
        if not (0 <= r < m and 0 <= c < n) or grid[r][c] == 0 or (r, c) in seen:
            return 0
        seen.add((r, c))
        return 1 + area(r + 1, c) + area(r - 1, c) + area(r, c + 1) + area(r, c - 1)

    return max(area(r, c) for r in range(m) for c in range(n))''',
            ),
            dict(
                name="Iterative flood fill with a stack",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                best=True,
                why=[
                    "An explicit stack does the same flood and counts cells as they are popped. Safe for any grid size.",
                ],
                code='''def max_area_of_island(grid):
    m, n = len(grid), len(grid[0])
    seen, best = set(), 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] and (r, c) not in seen:
                seen.add((r, c))
                stack, size = [(r, c)], 0
                while stack:
                    x, y = stack.pop()
                    size += 1
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            stack.append((nx, ny))
                best = max(best, size)
    return best''',
            ),
        ],
        tests='''g = [[0,0,1,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,1,1,0,1,0,0,0,0,0,0,0,0],[0,1,0,0,1,1,0,0,1,0,1,0,0],[0,1,0,0,1,1,0,0,1,1,1,0,0],[0,0,0,0,0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,0,0,0,0,0,0,1,1,0,0,0,0]]
assert max_area_of_island(g) == 6 and max_area_of_island([[0, 0]]) == 0 and max_area_of_island([[1]]) == 1''',
    ),

    # ------------------------------------------------------------------ 133
    dict(
        id="clone-graph",
        lc=133, slug="clone-graph",
        name="Clone Graph",
        difficulty="medium",
        framing=[
            "Deep-copy a connected undirected graph given one node. The graph has cycles, so a naive recursive copy loops forever; a map from original to copy both prevents that and supplies the copies needed to wire up neighbours.",
        ],
        approaches=[
            dict(
                name="DFS with an original &rarr; copy map",
                time="O(V + E)",
                space="O(V)",
                why=[
                    "<code>clone(node)</code> returns the existing copy if there is one; otherwise it creates the copy, <em>records it before recursing</em> (so a cycle back to this node finds it), then clones each neighbour into the copy's list.",
                ],
                code='''def clone_graph(node):
    copies = {}

    def clone(n):
        if n in copies:
            return copies[n]
        c = copies[n] = Node(n.val)            # record before recursing
        c.neighbors = [clone(nb) for nb in n.neighbors]
        return c

    return clone(node) if node else None''',
            ),
            dict(
                name="BFS with an original &rarr; copy map",
                time="O(V + E)",
                space="O(V)",
                best=True,
                why=[
                    "Create the start node's copy and enqueue the original. For each dequeued node, make copies of unseen neighbours (enqueueing them) and append each neighbour's copy to the current copy's list. Iterative, so no recursion depth issues on long chains.",
                ],
                code='''def clone_graph(node):
    if node is None:
        return None
    copies = {node: Node(node.val)}
    queue = deque([node])
    while queue:
        n = queue.popleft()
        for nb in n.neighbors:
            if nb not in copies:
                copies[nb] = Node(nb.val)
                queue.append(nb)
            copies[n].neighbors.append(copies[nb])
    return copies[node]''',
            ),
        ],
        tests='''class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def make(adj):
    nodes = [Node(i + 1) for i in range(len(adj))]
    for i, nbs in enumerate(adj):
        nodes[i].neighbors = [nodes[j - 1] for j in nbs]
    return nodes[0] if nodes else None


def dump(start):
    seen, order, q = {start}, [], deque([start])
    while q:
        x = q.popleft(); order.append(x)
        for y in x.neighbors:
            if y not in seen:
                seen.add(y); q.append(y)
    return sorted((x.val, sorted(y.val for y in x.neighbors)) for x in order), {id(x) for x in order}

for adj in ([[2, 4], [1, 3], [2, 4], [1, 3]], [[]], [[2], [1]]):
    g = make(adj)
    copy = clone_graph(g)
    (a, ids_a), (b, ids_b) = dump(g), dump(copy)
    assert a == b and not (ids_a & ids_b)
assert clone_graph(None) is None''',
    ),

    # ------------------------------------------------------------------ 286
    dict(
        id="walls-and-gates",
        lc=286, slug="walls-and-gates",
        name="Walls and Gates",
        difficulty="medium",
        tags=["Array", "Breadth-First Search", "Matrix"],
        statement=[
            "You are given an m &times; n grid where <code>-1</code> is a wall, <code>0</code> is a gate, and <code>INF = 2147483647</code> is an empty room. Fill each empty room <strong>in place</strong> with the distance to its nearest gate (moving up, down, left, right). Rooms that cannot reach a gate stay INF.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input="rooms = [[INF,-1,0,INF],[INF,INF,INF,-1],[INF,-1,INF,-1],[0,-1,INF,INF]]",
                 output="[[3,-1,0,1],[2,2,1,-1],[1,-1,2,-1],[0,-1,3,4]]"),
        ],
        constraints=["<code>1 &lt;= m, n &lt;= 250</code>"],
        approaches=[
            dict(
                name="BFS from every empty room",
                time="O((m &middot; n)&sup2;)",
                space="O(m &middot; n)",
                tag="brute force",
                why=[
                    "For each room, BFS outward until the first gate. Each BFS can cover the whole grid, and there are up to m &middot; n rooms.",
                ],
                code='''def walls_and_gates(rooms):
    INF = 2147483647
    m, n = len(rooms), len(rooms[0])
    original = [row[:] for row in rooms]
    for r in range(m):
        for c in range(n):
            if original[r][c] != INF:
                continue
            seen, q = {(r, c)}, deque([(r, c, 0)])
            while q:
                x, y, d = q.popleft()
                if original[x][y] == 0:
                    rooms[r][c] = d
                    break
                for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= a < m and 0 <= b < n and original[a][b] != -1 and (a, b) not in seen:
                        seen.add((a, b)); q.append((a, b, d + 1))''',
            ),
            dict(
                name="Multi-source BFS from all gates at once",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                best=True,
                why=[
                    "Put every gate in the queue at distance 0 and run one BFS. BFS reaches cells in order of distance, and since all gates start together, the first time a room is reached is from its <em>nearest</em> gate. Writing the distance into the room also marks it visited.",
                    "Every cell enters the queue at most once: O(m &middot; n) total, however many gates there are.",
                ],
                code='''def walls_and_gates(rooms):
    INF = 2147483647
    m, n = len(rooms), len(rooms[0])
    queue = deque((r, c) for r in range(m) for c in range(n) if rooms[r][c] == 0)
    while queue:
        r, c = queue.popleft()
        for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= a < m and 0 <= b < n and rooms[a][b] == INF:
                rooms[a][b] = rooms[r][c] + 1        # first visit = nearest gate
                queue.append((a, b))''',
            ),
        ],
        tests='''INF = 2147483647
R = [[INF, -1, 0, INF], [INF, INF, INF, -1], [INF, -1, INF, -1], [0, -1, INF, INF]]
walls_and_gates(R)
assert R == [[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]
R = [[-1]]; walls_and_gates(R); assert R == [[-1]]
R = [[INF, -1], [-1, 0]]; walls_and_gates(R); assert R == [[INF, -1], [-1, 0]]''',
    ),

    # ------------------------------------------------------------------ 994
    dict(
        id="rotting-oranges",
        lc=994, slug="rotting-oranges",
        name="Rotting Oranges",
        difficulty="medium",
        framing=[
            "Each minute, every rotten orange rots its fresh neighbours. How many minutes until none are fresh, or -1 if some never rot? The rot spreads from all rotten oranges simultaneously &mdash; multi-source BFS, counting levels.",
        ],
        approaches=[
            dict(
                name="Simulate minute by minute",
                time="O((m &middot; n)&sup2;)",
                space="O(m &middot; n)",
                why=[
                    "Each minute, scan the whole grid for fresh oranges next to rotten ones and rot them all at once (using a copy so newly rotten ones do not spread in the same minute). Stop when nothing changes. Up to m &middot; n minutes of O(m &middot; n) scans.",
                ],
                code='''def oranges_rotting(grid):
    g = [row[:] for row in grid]
    m, n = len(g), len(g[0])
    minutes = 0
    while True:
        rot = [(r, c) for r in range(m) for c in range(n) if g[r][c] == 1 and any(
            0 <= a < m and 0 <= b < n and g[a][b] == 2
            for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)))]
        if not rot:
            break
        for r, c in rot:
            g[r][c] = 2
        minutes += 1
    return -1 if any(1 in row for row in g) else minutes''',
            ),
            dict(
                name="Multi-source BFS by levels",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                best=True,
                why=[
                    "Start the queue with every rotten orange and count fresh ones. Process one level per minute; each fresh neighbour reached rots, decrements the fresh count and joins the next level. When the queue empties, any remaining fresh orange was unreachable.",
                ],
                code='''def oranges_rotting(grid):
    g = [row[:] for row in grid]
    m, n = len(g), len(g[0])
    queue = deque((r, c) for r in range(m) for c in range(n) if g[r][c] == 2)
    fresh = sum(row.count(1) for row in g)
    minutes = 0
    while queue and fresh:
        for _ in range(len(queue)):              # one minute
            r, c = queue.popleft()
            for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= a < m and 0 <= b < n and g[a][b] == 1:
                    g[a][b] = 2
                    fresh -= 1
                    queue.append((a, b))
        minutes += 1
    return -1 if fresh else minutes''',
            ),
        ],
        tests='''assert oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
assert oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
assert oranges_rotting([[0, 2]]) == 0 and oranges_rotting([[0]]) == 0
rng = random.Random(1)
for _ in range(40):
    m, n = rng.randint(1, 5), rng.randint(1, 5)
    g = [[rng.choice([0, 1, 1, 2]) for _ in range(n)] for _ in range(m)]
    h = [row[:] for row in g]; t = 0
    while True:
        rot = [(r, c) for r in range(m) for c in range(n) if h[r][c] == 1 and any(0 <= a < m and 0 <= b < n and h[a][b] == 2 for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)))]
        if not rot: break
        for r, c in rot: h[r][c] = 2
        t += 1
    assert oranges_rotting(g) == (-1 if any(1 in row for row in h) else t)''',
    ),

    # ------------------------------------------------------------------ 417
    dict(
        id="pacific-atlantic",
        lc=417, slug="pacific-atlantic-water-flow",
        name="Pacific Atlantic Water Flow",
        difficulty="medium",
        framing=[
            "Rain flows from a cell to a neighbour of equal or lower height. The Pacific touches the top and left edges, the Atlantic the bottom and right. Which cells can reach both oceans? Asking \"where can water from this cell go?\" per cell is expensive; asking \"which cells can reach this ocean?\" by flowing <em>uphill</em> from the ocean is two traversals total.",
        ],
        approaches=[
            dict(
                name="DFS from every cell",
                time="O((m &middot; n)&sup2;)",
                space="O(m &middot; n)",
                tag="brute force",
                why=["From each cell, explore downhill and record which oceans are touched. Each search can visit the whole grid."],
                code='''def pacific_atlantic(heights):
    m, n = len(heights), len(heights[0])
    out = []
    for r in range(m):
        for c in range(n):
            pac = atl = False
            seen, stack = {(r, c)}, [(r, c)]
            while stack and not (pac and atl):
                x, y = stack.pop()
                pac |= x == 0 or y == 0
                atl |= x == m - 1 or y == n - 1
                for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= a < m and 0 <= b < n and (a, b) not in seen and heights[a][b] <= heights[x][y]:
                        seen.add((a, b)); stack.append((a, b))
            if pac and atl:
                out.append([r, c])
    return out''',
            ),
            dict(
                name="Reverse flow: search uphill from each ocean",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                best=True,
                why=[
                    "Start a multi-source search from all Pacific-edge cells, moving to neighbours of <em>equal or greater</em> height: every cell reached can drain into the Pacific. Do the same from the Atlantic edges. The answer is the intersection. Each cell is visited at most twice.",
                ],
                code='''def pacific_atlantic(heights):
    m, n = len(heights), len(heights[0])

    def reach(starts):
        seen, stack = set(starts), list(starts)
        while stack:
            x, y = stack.pop()
            for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= a < m and 0 <= b < n and (a, b) not in seen and heights[a][b] >= heights[x][y]:
                    seen.add((a, b))
                    stack.append((a, b))
        return seen

    pacific = reach([(0, c) for c in range(n)] + [(r, 0) for r in range(m)])
    atlantic = reach([(m - 1, c) for c in range(n)] + [(r, n - 1) for r in range(m)])
    return sorted([r, c] for r, c in pacific & atlantic)''',
            ),
        ],
        tests='''H = [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]
assert sorted(pacific_atlantic(H)) == [[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]
assert pacific_atlantic([[1]]) == [[0, 0]]''',
    ),

    # ------------------------------------------------------------------ 130
    dict(
        id="surrounded-regions",
        lc=130, slug="surrounded-regions",
        name="Surrounded Regions",
        difficulty="medium",
        framing=[
            "Flip every region of 'O' that is completely surrounded by 'X' to 'X'. A region survives exactly when it touches the border. So instead of testing each region, mark everything reachable from border 'O's as safe, then flip the rest.",
        ],
        approaches=[
            dict(
                name="Explore each region, flip if it never touches the border",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                why=[
                    "Flood each unvisited 'O' region, remembering whether any of its cells is on the border; flip the region if not. Each cell is visited once, but every region must be collected before deciding.",
                ],
                code='''def solve(board):
    m, n = len(board), len(board[0])
    seen = set()
    for r in range(m):
        for c in range(n):
            if board[r][c] == "O" and (r, c) not in seen:
                region, border, stack = [], False, [(r, c)]
                seen.add((r, c))
                while stack:
                    x, y = stack.pop()
                    region.append((x, y))
                    border |= x in (0, m - 1) or y in (0, n - 1)
                    for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= a < m and 0 <= b < n and board[a][b] == "O" and (a, b) not in seen:
                            seen.add((a, b)); stack.append((a, b))
                if not border:
                    for x, y in region:
                        board[x][y] = "X"''',
            ),
            dict(
                name="Mark safe cells from the border, then flip",
                time="O(m &middot; n)",
                space="O(m &middot; n) worst stack",
                best=True,
                why=[
                    "Flood from every border 'O', temporarily marking reached cells as 'S' (safe). Then one sweep: remaining 'O's are surrounded, so flip them to 'X', and restore 'S' to 'O'. The marks live in the board itself, so no visited set is needed.",
                ],
                code='''def solve(board):
    m, n = len(board), len(board[0])
    stack = [(r, c) for r in range(m) for c in range(n)
             if (r in (0, m - 1) or c in (0, n - 1)) and board[r][c] == "O"]
    while stack:
        r, c = stack.pop()
        if 0 <= r < m and 0 <= c < n and board[r][c] == "O":
            board[r][c] = "S"                    # connected to the border
            stack += [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]
    for row in board:
        for c, v in enumerate(row):
            row[c] = "O" if v == "S" else "X"''',
            ),
        ],
        tests='''B = [list("XXXX"), list("XOOX"), list("XXOX"), list("XOXX")]
solve(B)
assert B == [list("XXXX"), list("XXXX"), list("XXXX"), list("XOXX")]
B = [["X"]]; solve(B); assert B == [["X"]]
B = [list("OO"), list("OO")]; solve(B); assert B == [list("OO"), list("OO")]''',
    ),

    # ------------------------------------------------------------------ 752
    dict(
        id="open-the-lock",
        lc=752, slug="open-the-lock",
        name="Open the Lock",
        difficulty="medium",
        framing=[
            "A 4-wheel lock starts at \"0000\"; each move turns one wheel one notch up or down (wrapping 9&harr;0). Avoid the dead-ends and reach the target in the fewest moves. The states form an implicit graph of 10,000 nodes with 8 edges each &mdash; unweighted shortest path, so BFS.",
        ],
        approaches=[
            dict(
                name="BFS from the start",
                time="O(10<sup>4</sup> &middot; 8)",
                space="O(10<sup>4</sup>)",
                why=[
                    "Level-by-level BFS over lock states, generating the 8 neighbours of each and skipping dead-ends and visited states. The first time the target is dequeued, its level is the answer.",
                ],
                code='''def open_lock(deadends, target):
    dead = set(deadends)
    if "0000" in dead:
        return -1
    seen, queue = {"0000"}, deque([("0000", 0)])
    while queue:
        state, moves = queue.popleft()
        if state == target:
            return moves
        for i in range(4):
            d = int(state[i])
            for nd in ((d + 1) % 10, (d - 1) % 10):
                nxt = state[:i] + str(nd) + state[i + 1:]
                if nxt not in seen and nxt not in dead:
                    seen.add(nxt)
                    queue.append((nxt, moves + 1))
    return -1''',
            ),
            dict(
                name="Bidirectional BFS",
                time="O(b<sup>d/2</sup>) in practice",
                space="O(b<sup>d/2</sup>)",
                best=True,
                why=[
                    "Grow a frontier from the start and one from the target, always expanding the smaller one, and stop when they touch. With branching factor b and distance d, each side only explores about b<sup>d/2</sup> states instead of b<sup>d</sup> &mdash; a large saving on big state spaces, and the standard follow-up for shortest-path puzzles.",
                ],
                code='''def open_lock(deadends, target):
    dead = set(deadends)
    if "0000" in dead or target in dead:
        return -1
    if target == "0000":
        return 0
    front, back, seen = {"0000"}, {target}, {"0000", target}
    moves = 0
    while front and back:
        if len(front) > len(back):
            front, back = back, front            # expand the smaller side
        moves += 1
        nxt_front = set()
        for state in front:
            for i in range(4):
                d = int(state[i])
                for nd in ((d + 1) % 10, (d - 1) % 10):
                    nxt = state[:i] + str(nd) + state[i + 1:]
                    if nxt in back:
                        return moves
                    if nxt not in seen and nxt not in dead:
                        seen.add(nxt)
                        nxt_front.add(nxt)
        front = nxt_front
    return -1''',
            ),
        ],
        tests='''assert open_lock(["0201", "0101", "0102", "1212", "2002"], "0202") == 6
assert open_lock(["8888"], "0009") == 1
assert open_lock(["8887", "8889", "8878", "8898", "8788", "8988", "7888", "9888"], "8888") == -1
assert open_lock(["0000"], "8888") == -1 and open_lock([], "0000") == 0''',
    ),
    ],
)


SECTION_TOPO = dict(
    id="topological",
    title="Dependencies and topological order",
    idea=[
        "A directed graph of prerequisites can be done in some order exactly when it has no cycle. <strong>Kahn's algorithm</strong> repeatedly removes nodes with no remaining prerequisites (in-degree 0); DFS instead emits a node after all its dependents are finished and reverses the list. Both detect a cycle as \"some nodes were never emitted\".",
    ],
    problems=[

    # ------------------------------------------------------------------ 207
    dict(
        id="course-schedule",
        lc=207, slug="course-schedule",
        name="Course Schedule",
        difficulty="medium",
        framing=[
            "Can all courses be finished given prerequisite pairs <code>[a, b]</code> (take b before a)? Exactly when the prerequisite graph has no directed cycle.",
        ],
        approaches=[
            dict(
                name="DFS with three colours",
                time="O(V + E)",
                space="O(V + E)",
                why=[
                    "Colour nodes white (unvisited), grey (on the current DFS path) and black (finished). Reaching a grey node means the path has looped back on itself: a cycle. Black nodes are known cycle-free and skipped, so each node is explored once.",
                    "Two colours are not enough: a node reached twice along <em>different</em> paths (a diamond) is not a cycle, and only the grey/black distinction tells the cases apart.",
                ],
                code='''def can_finish(num_courses, prerequisites):
    adj = defaultdict(list)
    for a, b in prerequisites:
        adj[b].append(a)
    WHITE, GREY, BLACK = 0, 1, 2
    color = [WHITE] * num_courses

    def has_cycle(u):
        color[u] = GREY
        for v in adj[u]:
            if color[v] == GREY or (color[v] == WHITE and has_cycle(v)):
                return True
        color[u] = BLACK
        return False

    return not any(color[u] == WHITE and has_cycle(u) for u in range(num_courses))''',
            ),
            dict(
                name="Kahn's algorithm (BFS on in-degrees)",
                time="O(V + E)",
                space="O(V + E)",
                best=True,
                why=[
                    "Count each course's prerequisites. Queue every course with none; taking a course reduces its dependents' counts, and any that reach zero join the queue. If every course is eventually taken, there is no cycle &mdash; courses on a cycle always keep a count of at least 1.",
                    "Iterative, so no recursion limits, and it produces an actual order for free (Course Schedule II).",
                ],
                code='''def can_finish(num_courses, prerequisites):
    adj, indeg = defaultdict(list), [0] * num_courses
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    queue = deque(u for u in range(num_courses) if indeg[u] == 0)
    taken = 0
    while queue:
        u = queue.popleft()
        taken += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return taken == num_courses''',
            ),
        ],
        tests='''assert can_finish(2, [[1, 0]]) is True and can_finish(2, [[1, 0], [0, 1]]) is False
assert can_finish(3, [[1, 0], [2, 0], [2, 1]]) is True and can_finish(1, []) is True
assert can_finish(4, [[1, 0], [2, 1], [3, 2], [1, 3]]) is False''',
    ),

    # ------------------------------------------------------------------ 210
    dict(
        id="course-schedule-ii",
        lc=210, slug="course-schedule-ii",
        name="Course Schedule II",
        difficulty="medium",
        framing=[
            "Return an order in which to take all courses, or an empty list if impossible &mdash; a topological sort. Any valid order is accepted.",
        ],
        approaches=[
            dict(
                name="DFS post-order, reversed",
                time="O(V + E)",
                space="O(V + E)",
                why=[
                    "Record a course when its DFS <em>finishes</em>, i.e. after every course depending on it has been recorded. That list has dependents before prerequisites, so reversing it gives a valid order. The grey colour detects cycles as before.",
                ],
                code='''def find_order(num_courses, prerequisites):
    adj = defaultdict(list)
    for a, b in prerequisites:
        adj[b].append(a)
    color, post = [0] * num_courses, []

    def dfs(u):
        color[u] = 1
        for v in adj[u]:
            if color[v] == 1 or (color[v] == 0 and not dfs(v)):
                return False
        color[u] = 2
        post.append(u)
        return True

    for u in range(num_courses):
        if color[u] == 0 and not dfs(u):
            return []
    return post[::-1]''',
            ),
            dict(
                name="Kahn's algorithm, emitting as courses become free",
                time="O(V + E)",
                space="O(V + E)",
                best=True,
                why=[
                    "The order in which Kahn's queue releases courses is itself a valid order. If fewer than V courses are released, a cycle blocked the rest and the answer is empty.",
                ],
                code='''def find_order(num_courses, prerequisites):
    adj, indeg = defaultdict(list), [0] * num_courses
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    queue = deque(u for u in range(num_courses) if indeg[u] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return order if len(order) == num_courses else []''',
            ),
        ],
        tests='''def valid(n, pre, order):
    pos = {c: i for i, c in enumerate(order)}
    return len(order) == n and all(pos[b] < pos[a] for a, b in pre)

assert valid(2, [[1, 0]], find_order(2, [[1, 0]]))
assert valid(4, [[1, 0], [2, 0], [3, 1], [3, 2]], find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]]))
assert find_order(2, [[0, 1], [1, 0]]) == [] and find_order(1, []) == [0]
rng = random.Random(2)
for _ in range(40):
    n = rng.randint(1, 7)
    perm = rng.sample(range(n), n)
    pre = [[perm[j], perm[i]] for i in range(n) for j in range(i + 1, n) if rng.random() < 0.3]
    assert valid(n, pre, find_order(n, pre))''',
    ),

    # ------------------------------------------------------------------ 1462
    dict(
        id="course-schedule-iv",
        lc=1462, slug="course-schedule-iv",
        name="Course Schedule IV",
        difficulty="medium",
        framing=[
            "Answer many queries \"is course u a prerequisite (direct or indirect) of v?\". That is reachability in a DAG. Answering each query with a fresh search is O(q &middot; (V + E)); precomputing the <strong>transitive closure</strong> makes every query O(1).",
        ],
        approaches=[
            dict(
                name="DFS per query",
                time="O(q &middot; (V + E))",
                space="O(V + E)",
                why=["For each query, search from u and check whether v is reached. No precomputation; slow when queries are many (up to 10<sup>4</sup>)."],
                code='''def check_if_prerequisite(n, prerequisites, queries):
    adj = defaultdict(list)
    for a, b in prerequisites:
        adj[a].append(b)

    def reaches(u, v):
        seen, stack = {u}, [u]
        while stack:
            x = stack.pop()
            if x == v:
                return True
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        return False

    return [reaches(u, v) for u, v in queries]''',
            ),
            dict(
                name="Floyd&ndash;Warshall transitive closure",
                time="O(V&sup3; + q)",
                space="O(V&sup2;)",
                why=[
                    "<code>reach[i][j] |= reach[i][k] and reach[k][j]</code> for every intermediate k. With V &le; 100 that is 10<sup>6</sup> steps, after which every query is a table lookup. Simple and robust.",
                ],
                code='''def check_if_prerequisite(n, prerequisites, queries):
    reach = [[False] * n for _ in range(n)]
    for a, b in prerequisites:
        reach[a][b] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                row_k = reach[k]
                row_i = reach[i]
                for j in range(n):
                    if row_k[j]:
                        row_i[j] = True
    return [reach[u][v] for u, v in queries]''',
            ),
            dict(
                name="Topological order with ancestor bitsets",
                time="O(V &middot; (V + E) / w + q)",
                space="O(V&sup2; / w)",
                best=True,
                why=[
                    "Process courses in topological order. Each course's set of prerequisites is the union, over its direct prerequisites p, of <code>{p} &cup; prereqs(p)</code> &mdash; already complete because p came earlier. Storing each set as a Python integer bitset makes the union a single <code>|</code> over w-bit machine words.",
                ],
                code='''def check_if_prerequisite(n, prerequisites, queries):
    adj, indeg = defaultdict(list), [0] * n
    for a, b in prerequisites:
        adj[a].append(b)
        indeg[b] += 1
    anc = [0] * n                                # bit u set: u is a prerequisite
    queue = deque(u for u in range(n) if indeg[u] == 0)
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            anc[v] |= anc[u] | (1 << u)
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return [bool(anc[v] >> u & 1) for u, v in queries]''',
            ),
        ],
        tests='''assert check_if_prerequisite(2, [[1, 0]], [[0, 1], [1, 0]]) == [False, True]
assert check_if_prerequisite(2, [], [[1, 0], [0, 1]]) == [False, False]
assert check_if_prerequisite(3, [[1, 2], [1, 0], [2, 0]], [[1, 0], [1, 2]]) == [True, True]
rng = random.Random(3)
for _ in range(30):
    n = rng.randint(2, 7)
    perm = rng.sample(range(n), n)
    pre = [[perm[i], perm[j]] for i in range(n) for j in range(i + 1, n) if rng.random() < 0.3]
    qs = [rng.sample(range(n), 2) for _ in range(10)]
    reach = {u: set() for u in range(n)}
    for _ in range(n):
        for a, b in pre:
            reach[a] |= {b} | reach[b]
    assert check_if_prerequisite(n, pre, qs) == [v in reach[u] for u, v in qs]''',
    ),

    # ------------------------------------------------------------------ 399
    dict(
        id="evaluate-division",
        lc=399, slug="evaluate-division",
        name="Evaluate Division",
        difficulty="medium",
        framing=[
            "Given equations <code>a / b = k</code>, answer queries <code>x / y</code> (or -1.0 if unknown). Treat variables as nodes and each equation as two weighted edges (a&rarr;b with k, b&rarr;a with 1/k). A query is the product of weights along any path from x to y.",
        ],
        approaches=[
            dict(
                name="DFS per query, multiplying weights",
                time="O(q &middot; (V + E))",
                space="O(V + E)",
                why=[
                    "Search from x, carrying the product of edge weights so far; reaching y gives the answer. Unknown variables or disconnected pairs give -1. Every query repeats a search.",
                ],
                code='''def calc_equation(equations, values, queries):
    graph = defaultdict(dict)
    for (a, b), k in zip(equations, values):
        graph[a][b] = k
        graph[b][a] = 1 / k

    def solve(x, y):
        if x not in graph or y not in graph:
            return -1.0
        seen, stack = {x}, [(x, 1.0)]
        while stack:
            node, prod = stack.pop()
            if node == y:
                return prod
            for nb, w in graph[node].items():
                if nb not in seen:
                    seen.add(nb); stack.append((nb, prod * w))
        return -1.0

    return [solve(x, y) for x, y in queries]''',
            ),
            dict(
                name="Weighted union-find",
                time="O((E + q) &middot; &alpha;)",
                space="O(V)",
                best=True,
                why=[
                    "Store for each variable its parent and <code>weight[v] = v / parent(v)</code>. <code>find</code> compresses paths while multiplying weights, so after it <code>weight[v] = v / root</code>. Union a and b by attaching one root under the other with the weight that makes <code>a / b = k</code> hold.",
                    "Then <code>x / y = weight[x] / weight[y]</code> when x and y share a root. Every query is near O(1), which pays off when queries are many.",
                ],
                code='''def calc_equation(equations, values, queries):
    parent, weight = {}, {}

    def find(x):
        if parent[x] != x:
            root = find(parent[x])
            weight[x] *= weight[parent[x]]         # x / root
            parent[x] = root
        return parent[x]

    for (a, b), k in zip(equations, values):
        for v in (a, b):
            if v not in parent:
                parent[v], weight[v] = v, 1.0
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            weight[ra] = k * weight[b] / weight[a]  # makes a / b == k

    out = []
    for x, y in queries:
        if x not in parent or y not in parent or find(x) != find(y):
            out.append(-1.0)
        else:
            out.append(weight[x] / weight[y])
    return out''',
            ),
        ],
        tests='''got = calc_equation([["a", "b"], ["b", "c"]], [2.0, 3.0], [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]])
assert [round(v, 6) for v in got] == [6.0, 0.5, -1.0, 1.0, -1.0]
got = calc_equation([["a", "b"], ["c", "d"]], [1.0, 1.0], [["a", "c"], ["b", "a"]])
assert got == [-1.0, 1.0]
got = calc_equation([["a", "b"], ["b", "c"], ["bc", "cd"]], [1.5, 2.5, 5.0], [["a", "c"], ["c", "b"], ["bc", "cd"], ["cd", "bc"]])
assert [round(v, 5) for v in got] == [3.75, 0.4, 5.0, 0.2]''',
    ),

    # ------------------------------------------------------------------ 310
    dict(
        id="minimum-height-trees",
        lc=310, slug="minimum-height-trees",
        name="Minimum Height Trees",
        difficulty="medium",
        framing=[
            "In a tree, which roots give the smallest height? Those roots are the <strong>centre</strong> of the tree &mdash; the middle one or two nodes of its longest path. Peeling leaves layer by layer converges on the centre.",
        ],
        approaches=[
            dict(
                name="BFS from every node",
                time="O(n&sup2;)",
                space="O(n)",
                tag="brute force",
                why=["Compute each root's height with a BFS and keep the minimum. Correct, and quadratic for n = 2 &times; 10<sup>4</sup>."],
                code='''def find_min_height_trees(n, edges):
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)

    def height(root):
        seen, frontier, h = {root}, [root], -1
        while frontier:
            h += 1
            nxt = []
            for u in frontier:
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v); nxt.append(v)
            frontier = nxt
        return h

    hs = [height(r) for r in range(n)]
    best = min(hs)
    return [r for r in range(n) if hs[r] == best]''',
            ),
            dict(
                name="Trim leaves layer by layer",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "A leaf is never a better root than its neighbour. Remove all current leaves at once, which creates new leaves, and repeat until at most two nodes remain. Those are the centres: every longest path loses one node from each end per round, so its middle survives last.",
                    "This is Kahn's algorithm run on an undirected tree, with degree 1 playing the role of in-degree 0.",
                ],
                code='''def find_min_height_trees(n, edges):
    if n <= 2:
        return list(range(n))
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    leaves = [u for u in range(n) if len(adj[u]) == 1]
    remaining = n
    while remaining > 2:
        remaining -= len(leaves)
        nxt = []
        for leaf in leaves:
            nb = adj[leaf].pop()
            adj[nb].discard(leaf)
            if len(adj[nb]) == 1:
                nxt.append(nb)
        leaves = nxt
    return sorted(leaves)''',
            ),
        ],
        tests='''assert find_min_height_trees(4, [[1, 0], [1, 2], [1, 3]]) == [1]
assert sorted(find_min_height_trees(6, [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]])) == [3, 4]
assert find_min_height_trees(1, []) == [0] and sorted(find_min_height_trees(2, [[0, 1]])) == [0, 1]
rng = random.Random(4)
for _ in range(40):
    n = rng.randint(1, 12)
    edges = [[i, rng.randrange(i)] for i in range(1, n)]
    adj = defaultdict(list)
    for a, b in edges: adj[a].append(b); adj[b].append(a)
    def h(r):
        seen, fr, d = {r}, [r], -1
        while fr:
            d += 1; nx = []
            for u in fr:
                for v in adj[u]:
                    if v not in seen: seen.add(v); nx.append(v)
            fr = nx
        return d
    hs = [h(r) for r in range(n)]
    assert sorted(find_min_height_trees(n, edges)) == [r for r in range(n) if hs[r] == min(hs)]''',
    ),

    # ------------------------------------------------------------------ 127
    dict(
        id="word-ladder",
        lc=127, slug="word-ladder",
        name="Word Ladder",
        difficulty="hard",
        framing=[
            "Transform <code>beginWord</code> into <code>endWord</code> one letter at a time, each intermediate word in the list. Return the number of words in the shortest sequence (0 if impossible). Words are nodes, one-letter differences are edges, and the question is an unweighted shortest path &mdash; BFS. The hard part is finding neighbours quickly.",
        ],
        approaches=[
            dict(
                name="Build the graph by comparing every pair",
                time="O(N&sup2; &middot; L)",
                space="O(N&sup2;)",
                tag="brute force",
                why=["Compare every pair of words for a one-letter difference to build an adjacency list, then BFS. With N = 5000 words, 12.5 million comparisons before the search even starts."],
                code='''def ladder_length(begin, end, word_list):
    words = list(dict.fromkeys([begin] + word_list))
    if end not in words:
        return 0
    adj = defaultdict(list)
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            if sum(a != b for a, b in zip(words[i], words[j])) == 1:
                adj[words[i]].append(words[j]); adj[words[j]].append(words[i])
    seen, queue = {begin}, deque([(begin, 1)])
    while queue:
        w, d = queue.popleft()
        if w == end:
            return d
        for nb in adj[w]:
            if nb not in seen:
                seen.add(nb); queue.append((nb, d + 1))
    return 0''',
            ),
            dict(
                name="BFS, generating neighbours by changing each letter",
                time="O(N &middot; L&sup2; &middot; 26)",
                space="O(N &middot; L)",
                why=[
                    "From each word, try all 26 letters at each of its L positions and keep the candidates that are in the word set. Building each candidate string costs O(L), so each word costs O(26 &middot; L&sup2;). Removing words from the set as they are enqueued doubles as the visited check.",
                ],
                code='''def ladder_length(begin, end, word_list):
    words = set(word_list)
    if end not in words:
        return 0
    queue = deque([(begin, 1)])
    words.discard(begin)
    while queue:
        w, d = queue.popleft()
        if w == end:
            return d
        for i in range(len(w)):
            for ch in "abcdefghijklmnopqrstuvwxyz":
                nxt = w[:i] + ch + w[i + 1:]
                if nxt in words:
                    words.remove(nxt)            # visited
                    queue.append((nxt, d + 1))
    return 0''',
            ),
            dict(
                name="Wildcard pattern buckets, bidirectional BFS",
                time="O(N &middot; L&sup2;)",
                space="O(N &middot; L&sup2;)",
                best=True,
                why=[
                    "Index every word under each of its L wildcard patterns (<code>hot &rarr; *ot, h*t, ho*</code>). Words sharing a pattern are exactly one letter apart, so neighbours come straight from the buckets with no 26-way loop.",
                    "Searching from both ends at once and always expanding the smaller frontier cuts the explored area dramatically on long ladders.",
                ],
                code='''def ladder_length(begin, end, word_list):
    words = set(word_list)
    if end not in words:
        return 0
    L = len(begin)
    buckets = defaultdict(list)
    for w in words | {begin}:
        for i in range(L):
            buckets[w[:i] + "*" + w[i + 1:]].append(w)
    front, back, seen, steps = {begin}, {end}, {begin, end}, 1
    while front and back:
        if len(front) > len(back):
            front, back = back, front
        steps += 1
        nxt = set()
        for w in front:
            for i in range(L):
                for nb in buckets[w[:i] + "*" + w[i + 1:]]:
                    if nb in back:
                        return steps
                    if nb not in seen:
                        seen.add(nb)
                        nxt.add(nb)
        front = nxt
    return 0''',
            ),
        ],
        tests='''assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
assert ladder_length("a", "c", ["a", "b", "c"]) == 2
assert ladder_length("hot", "dog", ["hot", "dog"]) == 0''',
    ),
    ],
)
