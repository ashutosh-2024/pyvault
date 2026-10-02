# -*- coding: utf-8 -*-
"""Graphs topic, part 2: shortest paths, spanning trees, Eulerian paths and
topological ordering puzzles (NeetCode 250: Advanced Graphs). Assembled into
GRAPHS_TOPIC by content/graphs.py."""

SECTION_WEIGHTED = dict(
    id="weighted",
    title="Shortest paths and minimax paths",
    idea=[
        "With edge weights, BFS no longer finds shortest paths. <strong>Dijkstra</strong> (a min-heap of tentative distances) handles non-negative weights in O(E log V); <strong>Bellman&ndash;Ford</strong> (relax every edge V - 1 times) handles negative weights and, usefully, limits on the number of edges. For \"minimise the worst step\" problems, Dijkstra works with <code>max</code> in place of <code>+</code>, and binary search on the answer or union-find over sorted edges work too.",
    ],
    problems=[

    # ------------------------------------------------------------------ 743
    dict(
        id="network-delay-time",
        lc=743, slug="network-delay-time",
        name="Network Delay Time",
        difficulty="medium",
        framing=[
            "A signal leaves node k along directed, weighted edges. How long until every node has it? That is the largest shortest-path distance from k &mdash; or -1 if some node is unreachable. The textbook single-source shortest path problem.",
        ],
        approaches=[
            dict(
                name="Bellman&ndash;Ford",
                time="O(V &middot; E)",
                space="O(V)",
                why=[
                    "Relax every edge (<code>dist[v] = min(dist[v], dist[u] + w)</code>) up to V - 1 times; a shortest path has at most V - 1 edges, so after that many rounds every distance is final. Simple, handles negative weights, and slow on dense graphs.",
                ],
                code='''def network_delay_time(times, n, k):
    dist = [float("inf")] * (n + 1)
    dist[k] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in times:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    best = max(dist[1:])
    return -1 if best == float("inf") else best''',
            ),
            dict(
                name="Floyd&ndash;Warshall",
                time="O(V&sup3;)",
                space="O(V&sup2;)",
                why=[
                    "All-pairs shortest paths via every intermediate node k. Wasteful for a single source, but with n &le; 100 it is only 10<sup>6</sup> steps and the code is three loops.",
                ],
                code='''def network_delay_time(times, n, k):
    INF = float("inf")
    d = [[INF] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][i] = 0
    for u, v, w in times:
        d[u][v] = min(d[u][v], w)
    for m in range(1, n + 1):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if d[i][m] + d[m][j] < d[i][j]:
                    d[i][j] = d[i][m] + d[m][j]
    best = max(d[k][1:])
    return -1 if best == INF else best''',
            ),
            dict(
                name="Dijkstra with a min-heap",
                time="O(E log V)",
                space="O(V + E)",
                best=True,
                why=[
                    "Pop the closest unsettled node from a heap; its distance is final, because every other route would pass through a node at least as far (weights are non-negative). Relax its outgoing edges, pushing improved distances. Skip stale heap entries for nodes already settled (\"lazy deletion\").",
                ],
                code='''def network_delay_time(times, n, k):
    adj = defaultdict(list)
    for u, v, w in times:
        adj[u].append((v, w))
    dist, heap = {}, [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue                              # stale entry
        dist[u] = d
        for v, w in adj[u]:
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return max(dist.values()) if len(dist) == n else -1''',
            ),
        ],
        tests='''assert network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2
assert network_delay_time([[1, 2, 1]], 2, 1) == 1 and network_delay_time([[1, 2, 1]], 2, 2) == -1
rng = random.Random(0)
for _ in range(40):
    n = rng.randint(1, 7)
    times = [[rng.randint(1, n), rng.randint(1, n), rng.randint(0, 9)] for _ in range(rng.randint(0, 15))]
    k = rng.randint(1, n)
    d = [float("inf")] * (n + 1); d[k] = 0
    for _ in range(n):
        for u, v, w in times:
            d[v] = min(d[v], d[u] + w)
    best = max(d[1:])
    assert network_delay_time(times, n, k) == (-1 if best == float("inf") else best)''',
    ),

    # ------------------------------------------------------------------ 1631
    dict(
        id="path-minimum-effort",
        lc=1631, slug="path-with-minimum-effort",
        name="Path With Minimum Effort",
        difficulty="medium",
        framing=[
            "Walk from the top-left to the bottom-right of a height grid. A path's effort is its <em>largest</em> single-step height difference. Minimise it. A minimax path problem: three standard techniques apply, and knowing all three is the point.",
        ],
        approaches=[
            dict(
                name="Binary search on the effort, BFS to test it",
                time="O(m &middot; n &middot; log H)",
                space="O(m &middot; n)",
                why=[
                    "\"Is there a path using only steps of difference &le; e?\" is monotonic in e and answered by one BFS. Binary-search e over <code>[0, max height]</code>.",
                ],
                code='''def minimum_effort_path(heights):
    m, n = len(heights), len(heights[0])

    def possible(limit):
        seen, queue = {(0, 0)}, deque([(0, 0)])
        while queue:
            r, c = queue.popleft()
            if (r, c) == (m - 1, n - 1):
                return True
            for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= a < m and 0 <= b < n and (a, b) not in seen and abs(heights[a][b] - heights[r][c]) <= limit:
                    seen.add((a, b)); queue.append((a, b))
        return False

    lo, hi = 0, max(map(max, heights))
    while lo < hi:
        mid = (lo + hi) // 2
        if possible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo''',
            ),
            dict(
                name="Union-find over edges sorted by difference",
                time="O(E log E)",
                space="O(m &middot; n)",
                why=[
                    "Sort all grid edges by height difference and add them in that order, uniting cells, until the start and end are connected. The last edge added is the answer: every path must use some edge at least that large, and this set of edges already connects them. (Kruskal's algorithm, stopped early.)",
                ],
                code='''def minimum_effort_path(heights):
    m, n = len(heights), len(heights[0])
    if m * n == 1:
        return 0
    edges = []
    for r in range(m):
        for c in range(n):
            if r + 1 < m:
                edges.append((abs(heights[r][c] - heights[r + 1][c]), r * n + c, (r + 1) * n + c))
            if c + 1 < n:
                edges.append((abs(heights[r][c] - heights[r][c + 1]), r * n + c, r * n + c + 1))
    parent = list(range(m * n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for w, a, b in sorted(edges):
        parent[find(a)] = find(b)
        if find(0) == find(m * n - 1):
            return w''',
            ),
            dict(
                name="Dijkstra with max instead of sum",
                time="O(m &middot; n &middot; log(m &middot; n))",
                space="O(m &middot; n)",
                best=True,
                why=[
                    "Run Dijkstra where a path's cost is the maximum step so far: extending to a neighbour costs <code>max(effort, |&Delta;h|)</code>. The greedy argument still holds because this cost never decreases along a path. The first time the target is popped, its effort is optimal.",
                ],
                code='''def minimum_effort_path(heights):
    m, n = len(heights), len(heights[0])
    best = [[float("inf")] * n for _ in range(m)]
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        e, r, c = heapq.heappop(heap)
        if (r, c) == (m - 1, n - 1):
            return e
        if e > best[r][c]:
            continue
        for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= a < m and 0 <= b < n:
                ne = max(e, abs(heights[a][b] - heights[r][c]))
                if ne < best[a][b]:
                    best[a][b] = ne
                    heapq.heappush(heap, (ne, a, b))''',
            ),
        ],
        tests='''assert minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]]) == 2
assert minimum_effort_path([[1, 2, 3], [3, 8, 4], [5, 3, 5]]) == 1
assert minimum_effort_path([[1, 2, 1, 1, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1], [1, 1, 1, 2, 1]]) == 0
assert minimum_effort_path([[7]]) == 0''',
    ),

    # ------------------------------------------------------------------ 778
    dict(
        id="swim-rising-water",
        lc=778, slug="swim-in-rising-water",
        name="Swim In Rising Water",
        difficulty="hard",
        framing=[
            "At time t you can swim between adjacent cells whose elevations are both &le; t. What is the earliest time you can get from the top-left to the bottom-right corner? The answer is the smallest possible <em>maximum elevation</em> along a path &mdash; the same minimax shape as the previous problem, on cells instead of edges.",
        ],
        approaches=[
            dict(
                name="Binary search on time, BFS to test it",
                time="O(n&sup2; log n&sup2;)",
                space="O(n&sup2;)",
                why=[
                    "At time t the usable cells are those with elevation &le; t; test connectivity with BFS and binary-search the smallest t that works. Elevations are a permutation of 0..n&sup2; - 1, so that is the search range.",
                ],
                code='''def swim_in_water(grid):
    n = len(grid)

    def possible(t):
        if grid[0][0] > t:
            return False
        seen, stack = {(0, 0)}, [(0, 0)]
        while stack:
            r, c = stack.pop()
            if (r, c) == (n - 1, n - 1):
                return True
            for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= a < n and 0 <= b < n and (a, b) not in seen and grid[a][b] <= t:
                    seen.add((a, b)); stack.append((a, b))
        return False

    lo, hi = 0, n * n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if possible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo''',
            ),
            dict(
                name="Dijkstra on the maximum elevation so far",
                time="O(n&sup2; log n)",
                space="O(n&sup2;)",
                best=True,
                why=[
                    "Always expand the reachable cell with the lowest elevation. The time needed so far is the maximum elevation popped along the way; when the corner is popped, that maximum is the answer. This is Prim's algorithm growing from the start, stopped at the target.",
                ],
                code='''def swim_in_water(grid):
    n = len(grid)
    seen, heap, t = {(0, 0)}, [(grid[0][0], 0, 0)], 0
    while heap:
        h, r, c = heapq.heappop(heap)
        t = max(t, h)
        if (r, c) == (n - 1, n - 1):
            return t
        for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= a < n and 0 <= b < n and (a, b) not in seen:
                seen.add((a, b))
                heapq.heappush(heap, (grid[a][b], a, b))''',
            ),
            dict(
                name="Union-find, adding cells in order of elevation",
                time="O(n&sup2; &middot; &alpha;)",
                space="O(n&sup2;)",
                why=[
                    "Because elevations are a permutation, cell positions can be indexed by elevation directly &mdash; no sort needed. Switch cells on in increasing elevation, uniting each with already-on neighbours, and stop at the first time t when the two corners are in the same set.",
                ],
                code='''def swim_in_water(grid):
    n = len(grid)
    where = [None] * (n * n)
    for r in range(n):
        for c in range(n):
            where[grid[r][c]] = (r, c)
    parent = list(range(n * n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for t in range(n * n):
        r, c = where[t]
        for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= a < n and 0 <= b < n and grid[a][b] <= t:
                parent[find(r * n + c)] = find(a * n + b)
        if find(0) == find(n * n - 1):
            return t''',
            ),
        ],
        tests='''assert swim_in_water([[0, 2], [1, 3]]) == 3
g = [[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]
assert swim_in_water(g) == 16 and swim_in_water([[0]]) == 0
rng = random.Random(1)
for _ in range(30):
    n = rng.randint(1, 5)
    vals = rng.sample(range(n * n), n * n)
    g = [vals[i * n:(i + 1) * n] for i in range(n)]
    best = None
    for t in range(n * n):
        if g[0][0] > t: continue
        seen, st = {(0, 0)}, [(0, 0)]
        while st:
            r, c = st.pop()
            for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= a < n and 0 <= b < n and (a, b) not in seen and g[a][b] <= t:
                    seen.add((a, b)); st.append((a, b))
        if (n - 1, n - 1) in seen:
            best = t; break
    assert swim_in_water(g) == best''',
    ),

    # ------------------------------------------------------------------ 787
    dict(
        id="cheapest-flights-k-stops",
        lc=787, slug="cheapest-flights-within-k-stops",
        name="Cheapest Flights Within K Stops",
        difficulty="medium",
        framing=[
            "Cheapest price from <code>src</code> to <code>dst</code> using at most k stops (k + 1 flights). The stop limit breaks plain Dijkstra: the cheapest way to reach an intermediate city may use too many stops, while a pricier route with fewer stops is the one that can continue. Bellman&ndash;Ford's rounds count edges naturally.",
        ],
        pitfall="Standard Dijkstra that settles each city once by price. It can lock in a cheap route that has already used up the stop budget.",
        approaches=[
            dict(
                name="Bellman&ndash;Ford, k + 1 rounds",
                time="O(k &middot; E)",
                space="O(V)",
                best=True,
                why=[
                    "After round i, <code>price[v]</code> is the cheapest cost to reach v with at most i flights. Each round relaxes every flight <em>from a copy of the previous round's prices</em>, so a single round never chains two flights. k + 1 rounds give the answer.",
                    "The copy is the whole trick: without it, one round could use several flights and the stop limit would be violated.",
                ],
                code='''def find_cheapest_price(n, flights, src, dst, k):
    INF = float("inf")
    price = [INF] * n
    price[src] = 0
    for _ in range(k + 1):
        prev = price[:]                          # read only last round's prices
        for u, v, w in flights:
            if prev[u] + w < price[v]:
                price[v] = prev[u] + w
    return -1 if price[dst] == INF else price[dst]''',
            ),
            dict(
                name="BFS by number of flights, with pruning",
                time="O(k &middot; E)",
                space="O(V + E)",
                why=[
                    "Process level by level (one level per flight), carrying (city, cost). Only push a city if this cost beats the best known cost for it &mdash; a cheaper cost with the same or fewer flights dominates. Stop after k + 1 levels.",
                ],
                code='''def find_cheapest_price(n, flights, src, dst, k):
    adj = defaultdict(list)
    for u, v, w in flights:
        adj[u].append((v, w))
    best = [float("inf")] * n
    best[src] = 0
    level = [(src, 0)]
    for _ in range(k + 1):
        nxt = []
        for u, cost in level:
            for v, w in adj[u]:
                if cost + w < best[v]:
                    best[v] = cost + w
                    nxt.append((v, cost + w))
        level = nxt
    return -1 if best[dst] == float("inf") else best[dst]''',
            ),
            dict(
                name="Dijkstra on (city, flights used)",
                time="O(k &middot; E log(k &middot; V))",
                space="O(k &middot; V)",
                why=[
                    "Make the state (city, flights so far); then Dijkstra is correct again. Pop the cheapest state; the first time dst is popped is the answer. Prune a state if the city was already reached with fewer flights at no greater cost.",
                ],
                code='''def find_cheapest_price(n, flights, src, dst, k):
    adj = defaultdict(list)
    for u, v, w in flights:
        adj[u].append((v, w))
    fewest = [float("inf")] * n                  # fewest flights seen per city
    heap = [(0, src, 0)]
    while heap:
        cost, u, used = heapq.heappop(heap)
        if u == dst:
            return cost
        if used >= fewest[u] or used > k:
            continue
        fewest[u] = used
        for v, w in adj[u]:
            heapq.heappush(heap, (cost + w, v, used + 1))
    return -1''',
            ),
        ],
        tests='''assert find_cheapest_price(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1) == 700
assert find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1) == 200
assert find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0) == 500
rng = random.Random(2)
for _ in range(60):
    n = rng.randint(2, 6)
    fl = list({(u, v): [u, v, rng.randint(1, 20)] for u, v in ((rng.randrange(n), rng.randrange(n)) for _ in range(12)) if u != v}.values())
    s, d = rng.sample(range(n), 2); k = rng.randint(0, 3)
    best = float("inf")
    def go(u, cost, stops):
        global best
        if u == d:
            best = min(best, cost); return
        if stops > k: return
        for a, b, w in fl:
            if a == u: go(b, cost + w, stops + 1)
    go(s, 0, 0)
    assert find_cheapest_price(n, fl, s, d, k) == (-1 if best == float("inf") else best)''',
    ),
    ],
)


SECTION_STRUCTURE = dict(
    id="graph-structure",
    title="Spanning trees, Euler paths and orderings",
    idea=[
        "A <strong>minimum spanning tree</strong> connects every node at least total cost: Kruskal adds the cheapest edges that do not form a cycle (union-find), Prim grows one tree from a node (a heap, or an O(V&sup2;) array on dense graphs). An <strong>Eulerian path</strong> uses every edge once, found by Hierholzer's algorithm. And ordering constraints &mdash; alien alphabets, matrix rows and columns &mdash; are topological sorts in disguise.",
    ],
    problems=[

    # ------------------------------------------------------------------ 332
    dict(
        id="reconstruct-itinerary",
        lc=332, slug="reconstruct-itinerary",
        name="Reconstruct Itinerary",
        difficulty="hard",
        framing=[
            "Use every ticket exactly once, starting from \"JFK\", and return the lexicographically smallest valid itinerary. Using every edge exactly once is an <strong>Eulerian path</strong>. Greedily taking the smallest destination can dead-end, which is why the naive approach needs backtracking and the right one needs Hierholzer's algorithm.",
        ],
        approaches=[
            dict(
                name="DFS with backtracking, smallest destination first",
                time="O(E<sup>d</sup>) worst",
                space="O(E)",
                why=[
                    "Try destinations in sorted order, removing the ticket before recursing and restoring it if the branch cannot use every ticket. The first complete itinerary found is the smallest. Usually fast; exponential on adversarial inputs.",
                ],
                code='''def find_itinerary(tickets):
    adj = defaultdict(list)
    for a, b in sorted(tickets):
        adj[a].append(b)
    route = ["JFK"]

    def dfs(airport):
        if len(route) == len(tickets) + 1:
            return True
        for i, nxt in enumerate(adj[airport]):
            if nxt is None:
                continue
            adj[airport][i] = None               # use the ticket
            route.append(nxt)
            if dfs(nxt):
                return True
            route.pop()
            adj[airport][i] = nxt                # give it back
        return False

    dfs("JFK")
    return route''',
            ),
            dict(
                name="Hierholzer's algorithm",
                time="O(E log E)",
                space="O(E)",
                best=True,
                why=[
                    "Keep each airport's destinations in a min-heap (or a reverse-sorted list used as a stack). Walk greedily, always taking the smallest ticket; when an airport has no tickets left, it must be the end of whatever remains of the route, so append it to the answer and back up. Reverse the answer at the end.",
                    "A dead end is not a failure here: it is the tail of the route, and the detours discovered on the way back get spliced in ahead of it. Each ticket is used once, so the work is linear after sorting.",
                ],
                code='''def find_itinerary(tickets):
    adj = defaultdict(list)
    for a, b in sorted(tickets, reverse=True):
        adj[a].append(b)                         # pop() yields the smallest
    route, stack = [], ["JFK"]
    while stack:
        while adj[stack[-1]]:
            stack.append(adj[stack[-1]].pop())
        route.append(stack.pop())                # stuck: this is the tail
    return route[::-1]''',
            ),
        ],
        tests='''assert find_itinerary([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]) == ["JFK", "MUC", "LHR", "SFO", "SJC"]
assert find_itinerary([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]) == ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]
assert find_itinerary([["JFK", "KUL"], ["JFK", "NRT"], ["NRT", "JFK"]]) == ["JFK", "NRT", "JFK", "KUL"]''',
    ),

    # ------------------------------------------------------------------ 1584
    dict(
        id="min-cost-connect-points",
        lc=1584, slug="min-cost-to-connect-all-points",
        name="Min Cost to Connect All Points",
        difficulty="medium",
        framing=[
            "Connect all points with Manhattan-distance edges at minimum total cost: a minimum spanning tree of the complete graph. With n &le; 1000 there are about 500,000 edges, which makes the choice between Kruskal and Prim's variants matter.",
        ],
        approaches=[
            dict(
                name="Kruskal: sort all edges, union-find",
                time="O(n&sup2; log n)",
                space="O(n&sup2;)",
                why=[
                    "Build all n(n-1)/2 edges, sort them, and add each one that joins two different components until n - 1 have been added. Correct and general, but materialises and sorts every edge.",
                ],
                code='''def min_cost_connect_points(points):
    n = len(points)
    edges = sorted((abs(x1 - x2) + abs(y1 - y2), i, j)
                   for i, (x1, y1) in enumerate(points)
                   for j, (x2, y2) in enumerate(points) if i < j)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = used = 0
    for w, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
            total += w
            used += 1
            if used == n - 1:
                break
    return total''',
            ),
            dict(
                name="Prim with a min-heap",
                time="O(n&sup2; log n)",
                space="O(n&sup2;)",
                why=[
                    "Grow a tree from point 0: pop the cheapest edge to an unvisited point, add it, and push that point's edges to every other unvisited point. Lazy deletion skips edges to points already in the tree.",
                ],
                code='''def min_cost_connect_points(points):
    n = len(points)
    seen, heap, total = set(), [(0, 0)], 0
    while len(seen) < n:
        w, i = heapq.heappop(heap)
        if i in seen:
            continue
        seen.add(i)
        total += w
        xi, yi = points[i]
        for j, (xj, yj) in enumerate(points):
            if j not in seen:
                heapq.heappush(heap, (abs(xi - xj) + abs(yi - yj), j))
    return total''',
            ),
            dict(
                name="Prim with a distance array (dense graphs)",
                time="O(n&sup2;)",
                space="O(n)",
                best=True,
                why=[
                    "On a complete graph, keep <code>dist[j]</code> = cheapest edge from the tree to j. Each step picks the unvisited point with the smallest dist by a linear scan and updates every other point's dist from it. n steps of O(n): O(n&sup2;), no heap and no edge list &mdash; optimal for dense graphs.",
                ],
                code='''def min_cost_connect_points(points):
    n = len(points)
    dist = [float("inf")] * n
    dist[0] = 0
    in_tree = [False] * n
    total = 0
    for _ in range(n):
        i = min((d, j) for j, d in enumerate(dist) if not in_tree[j])[1]
        in_tree[i] = True
        total += dist[i]
        xi, yi = points[i]
        for j in range(n):
            if not in_tree[j]:
                d = abs(xi - points[j][0]) + abs(yi - points[j][1])
                if d < dist[j]:
                    dist[j] = d
    return total''',
            ),
        ],
        tests='''assert min_cost_connect_points([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]) == 20
assert min_cost_connect_points([[3, 12], [-2, 5], [-4, 1]]) == 18 and min_cost_connect_points([[0, 0]]) == 0
rng = random.Random(3)
for _ in range(20):
    pts = [[rng.randint(-10, 10), rng.randint(-10, 10)] for _ in range(rng.randint(1, 8))]
    n = len(pts)
    d = [[abs(a[0] - b[0]) + abs(a[1] - b[1]) for b in pts] for a in pts]
    INF = float("inf"); dist = [INF] * n; dist[0] = 0; used = [False] * n; tot = 0
    for _ in range(n):
        i = min((dist[j], j) for j in range(n) if not used[j])[1]; used[i] = True; tot += dist[i]
        for j in range(n):
            if not used[j]: dist[j] = min(dist[j], d[i][j])
    assert min_cost_connect_points(pts) == tot''',
    ),

    # ------------------------------------------------------------------ 269
    dict(
        id="alien-dictionary",
        lc=269, slug="alien-dictionary",
        name="Alien Dictionary",
        difficulty="hard",
        tags=["Array", "String", "Depth-First Search", "Breadth-First Search", "Graph", "Topological Sort"],
        statement=[
            "An alien language uses lowercase English letters in an unknown order. You are given a list of words <strong>sorted lexicographically</strong> by that order. Return a string containing every letter that appears, in an order consistent with the words. If the words are inconsistent with any order, return <code>\"\"</code>. If several orders are valid, return any of them.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input='words = ["wrt","wrf","er","ett","rftt"]', output='"wertf"'),
            dict(input='words = ["z","x","z"]', output='""', explanation="z before x and x before z: a cycle."),
            dict(input='words = ["abc","ab"]', output='""', explanation="A longer word cannot come before its own prefix."),
        ],
        constraints=[
            "<code>1 &lt;= words.length &lt;= 100</code>, <code>1 &lt;= words[i].length &lt;= 100</code>",
        ],
        pitfall="Missing the prefix case: <code>[\"abc\", \"ab\"]</code> gives no letter comparison at all, yet is impossible in any order.",
        approaches=[
            dict(
                name="Adjacent-pair edges, DFS post-order",
                time="O(C)",
                space="O(1) (at most 26 letters)",
                why=[
                    "Only adjacent words give information, and only at their first differing letter: <code>a[i]</code> comes before <code>b[i]</code>. Add those edges, then run a three-colour DFS; emitting letters on finish and reversing gives a topological order, and a grey-node hit means a cycle. C is the total number of characters.",
                ],
                code='''def alien_order(words):
    adj = {ch: set() for w in words for ch in w}
    for a, b in zip(words, words[1:]):
        for x, y in zip(a, b):
            if x != y:
                adj[x].add(y)
                break
        else:
            if len(a) > len(b):
                return ""                            # prefix after its extension
    color, out = {}, []

    def dfs(u):
        color[u] = 1
        for v in adj[u]:
            if color.get(v) == 1 or (v not in color and not dfs(v)):
                return False
        color[u] = 2
        out.append(u)
        return True

    for ch in adj:
        if ch not in color and not dfs(ch):
            return ""
    return "".join(reversed(out))''',
            ),
            dict(
                name="Adjacent-pair edges, Kahn's algorithm",
                time="O(C)",
                space="O(1) (at most 26 letters)",
                best=True,
                why=[
                    "Same edges, then Kahn: repeatedly output a letter with no remaining predecessors. If fewer letters come out than exist, the constraints contain a cycle. Iterative, and easy to adapt to \"return the lexicographically smallest order\" by swapping the queue for a heap.",
                ],
                code='''def alien_order(words):
    adj = {ch: set() for w in words for ch in w}
    indeg = {ch: 0 for ch in adj}
    for a, b in zip(words, words[1:]):
        for x, y in zip(a, b):
            if x != y:
                if y not in adj[x]:
                    adj[x].add(y)
                    indeg[y] += 1
                break
        else:
            if len(a) > len(b):
                return ""
    queue = deque(ch for ch in adj if indeg[ch] == 0)
    out = []
    while queue:
        u = queue.popleft()
        out.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return "".join(out) if len(out) == len(adj) else ""''',
            ),
        ],
        tests='''def consistent(words, order):
    if sorted(order) != sorted({c for w in words for c in w}) or len(order) != len(set(order)):
        return False
    rank = {c: i for i, c in enumerate(order)}
    key = lambda w: [rank[c] for c in w]
    return all(key(a) <= key(b) for a, b in zip(words, words[1:]))

assert consistent(["wrt", "wrf", "er", "ett", "rftt"], alien_order(["wrt", "wrf", "er", "ett", "rftt"]))
assert alien_order(["z", "x", "z"]) == "" and alien_order(["abc", "ab"]) == ""
assert sorted(alien_order(["z", "z"])) == ["z"]
rng = random.Random(4)
for _ in range(40):
    letters = rng.sample("abcdef", rng.randint(1, 6))
    rank = {c: i for i, c in enumerate(letters)}
    words = sorted({"".join(rng.choice(letters) for _ in range(rng.randint(1, 4))) for _ in range(6)},
                   key=lambda w: [rank[c] for c in w])
    assert consistent(words, alien_order(words))''',
    ),

    # ------------------------------------------------------------------ 1489
    dict(
        id="critical-pseudo-critical-edges",
        lc=1489, slug="find-critical-and-pseudo-critical-edges-in-minimum-spanning-tree",
        name="Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree",
        difficulty="hard",
        framing=[
            "An edge is <strong>critical</strong> if every MST contains it (removing it makes the MST heavier, or disconnects the graph), and <strong>pseudo-critical</strong> if some MSTs contain it and some do not. Both tests reduce to running Kruskal with one edge excluded or forced in.",
        ],
        approaches=[
            dict(
                name="Kruskal once per edge, excluded and forced",
                time="O(E&sup2; &middot; &alpha;(V))",
                space="O(V + E)",
                best=True,
                why=[
                    "Compute the MST weight W once. For each edge e: run Kruskal <em>without</em> e &mdash; if the result is heavier than W (or not spanning), e is critical. Otherwise run Kruskal with e <em>forced in first</em> &mdash; if the result still weighs W, some MST contains e, so it is pseudo-critical.",
                    "Sort the edges once and reuse the order in every run, so each run is a linear pass with union-find. With E &le; 200 that is fast. (A near-linear solution exists using bridges on the graph of equal-weight edges, but it is rarely expected.)",
                ],
                code='''def find_critical_and_pseudo_critical_edges(n, edges):
    order = sorted(range(len(edges)), key=lambda i: edges[i][2])

    def mst(skip=None, force=None):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        weight = used = 0
        if force is not None:
            a, b, w = edges[force]
            parent[find(a)] = find(b)
            weight, used = w, 1
        for i in order:
            if i == skip:
                continue
            a, b, w = edges[i]
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                weight += w
                used += 1
        return weight if used == n - 1 else float("inf")

    best = mst()
    critical, pseudo = [], []
    for i in range(len(edges)):
        if mst(skip=i) > best:
            critical.append(i)
        elif mst(force=i) == best:
            pseudo.append(i)
    return [critical, pseudo]''',
            ),
        ],
        tests='''got = find_critical_and_pseudo_critical_edges(5, [[0, 1, 1], [1, 2, 1], [2, 3, 2], [0, 3, 2], [0, 4, 3], [3, 4, 3], [1, 4, 6]])
assert [sorted(got[0]), sorted(got[1])] == [[0, 1], [2, 3, 4, 5]]
got = find_critical_and_pseudo_critical_edges(4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 1]])
assert [sorted(got[0]), sorted(got[1])] == [[], [0, 1, 2, 3]]''',
    ),

    # ------------------------------------------------------------------ 2392
    dict(
        id="build-matrix-conditions",
        lc=2392, slug="build-a-matrix-with-conditions",
        name="Build a Matrix With Conditions",
        difficulty="hard",
        framing=[
            "Place the numbers 1..k in a k &times; k matrix (one per row and column, rest 0) so that <code>above</code> pairs appear in strictly earlier rows and <code>left</code> pairs in strictly earlier columns. Rows and columns are independent: each is a topological sort of its own constraints. If either has a cycle, no matrix exists.",
        ],
        approaches=[
            dict(
                name="Two topological sorts with DFS",
                time="O(k + n)",
                space="O(k + n)",
                why=[
                    "Topologically sort 1..k under the row conditions and, separately, under the column conditions, with three-colour DFS (a grey hit means a cycle). The position of each number in the row order is its row; in the column order, its column.",
                ],
                code='''def build_matrix(k, row_conditions, col_conditions):
    def topo(conds):
        adj = defaultdict(list)
        for a, b in conds:
            adj[a].append(b)
        color, out = [0] * (k + 1), []

        def dfs(u):
            color[u] = 1
            for v in adj[u]:
                if color[v] == 1 or (color[v] == 0 and not dfs(v)):
                    return False
            color[u] = 2
            out.append(u)
            return True

        for u in range(1, k + 1):
            if color[u] == 0 and not dfs(u):
                return None
        return out[::-1]

    rows, cols = topo(row_conditions), topo(col_conditions)
    if rows is None or cols is None:
        return []
    r_of = {v: i for i, v in enumerate(rows)}
    c_of = {v: i for i, v in enumerate(cols)}
    M = [[0] * k for _ in range(k)]
    for v in range(1, k + 1):
        M[r_of[v]][c_of[v]] = v
    return M''',
            ),
            dict(
                name="Two topological sorts with Kahn's algorithm",
                time="O(k + n)",
                space="O(k + n)",
                best=True,
                why=[
                    "The same plan with Kahn's algorithm for each dimension: an order shorter than k signals a cycle. Iterative, and the two sorts share one helper.",
                ],
                code='''def build_matrix(k, row_conditions, col_conditions):
    def topo(conds):
        adj, indeg = defaultdict(list), [0] * (k + 1)
        for a, b in conds:
            adj[a].append(b)
            indeg[b] += 1
        queue = deque(v for v in range(1, k + 1) if indeg[v] == 0)
        out = []
        while queue:
            u = queue.popleft()
            out.append(u)
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    queue.append(v)
        return out if len(out) == k else None

    rows, cols = topo(row_conditions), topo(col_conditions)
    if rows is None or cols is None:
        return []
    r_of = {v: i for i, v in enumerate(rows)}
    c_of = {v: i for i, v in enumerate(cols)}
    M = [[0] * k for _ in range(k)]
    for v in range(1, k + 1):
        M[r_of[v]][c_of[v]] = v
    return M''',
            ),
        ],
        tests='''def check(k, rc, cc, M):
    pos = {M[r][c]: (r, c) for r in range(k) for c in range(k) if M[r][c]}
    return sorted(pos) == list(range(1, k + 1)) and all(pos[a][0] < pos[b][0] for a, b in rc) and all(pos[a][1] < pos[b][1] for a, b in cc)

assert check(3, [[1, 2], [3, 2]], [[2, 1], [3, 2]], build_matrix(3, [[1, 2], [3, 2]], [[2, 1], [3, 2]]))
assert build_matrix(3, [[1, 2], [2, 3], [3, 1], [2, 3]], [[2, 1]]) == []
rng = random.Random(5)
for _ in range(40):
    k = rng.randint(1, 6)
    pr, pc = rng.sample(range(1, k + 1), k), rng.sample(range(1, k + 1), k)
    rc = [[pr[i], pr[j]] for i in range(k) for j in range(i + 1, k) if rng.random() < 0.3]
    cc = [[pc[i], pc[j]] for i in range(k) for j in range(i + 1, k) if rng.random() < 0.3]
    assert check(k, rc, cc, build_matrix(k, rc, cc))''',
    ),
    ],
)
