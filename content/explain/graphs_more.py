"""Write-ups for the Graphs topic, part 2: topological sort, weighted graphs, graph structure."""

EXPLAIN = {
    # ------------------------------------------------------------------ course schedule
    "course-schedule": {
        "example": {"call": "can_finish(4, [[1, 0], [2, 1], [3, 2], [1, 3]])", "expect": "False"},
        "approaches": {
            "DFS with three colours": {
                "idea": [
                    "Courses are nodes and \"take b before a\" is an edge b → a. All courses can be finished exactly when this graph has no cycle.",
                    "During DFS, colour nodes white (unvisited), grey (on the current path) and black (finished).",
                    "Reaching a grey node means the path has looped back on itself. Black nodes are already known to be cycle-free and are skipped.",
                ],
                "steps": [
                    "<code>has_cycle(u)</code>: grey u; for each neighbour, a grey one is a cycle, and a white one is explored recursively; then black u.",
                    "Run it from every white node.",
                ],
                "why": [
                    "A plain visited flag cannot tell a cycle from a diamond (one node reached by two paths); grey versus black can.",
                    "Each node is explored once: O(V + E).",
                ],
                "dry": [
                    "Edges: 0 → 1, 1 → 2, 2 → 3, 3 → 1.",
                    "DFS from 0: 0, 1, 2 and 3 all turn grey as the path goes deeper.",
                    "From 3, the neighbour 1 is grey, so the path has looped: a cycle.",
                    "The result is <strong>False</strong>.",
                ],
            },
            "Kahn's algorithm (BFS on in-degrees)": {
                "idea": [
                    "Count each course's unmet prerequisites (its in-degree). Courses with none can be taken now.",
                    "Taking a course lowers its dependents' counts, and any that reach zero become available.",
                    "Courses on a cycle never reach zero, so if not every course gets taken, there is a cycle.",
                ],
                "steps": [
                    "Queue the courses with in-degree 0.",
                    "Pop, count it as taken, decrement its dependents, and queue any that hit 0.",
                    "Return <code>taken == num_courses</code>.",
                ],
                "why": [
                    "It is iterative, O(V + E), and the order it produces solves Course Schedule II.",
                ],
                "dry": [
                    "In-degrees: 1 has 2 (from 0 and 3), 2 has 1, 3 has 1. Only course 0 is free.",
                    "Take 0: course 1 drops to 1, still blocked by 3.",
                    "The queue is empty after taking 1 course out of 4.",
                    "The result is <strong>False</strong>: 1, 2 and 3 block each other in a cycle.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ course schedule II
    "course-schedule-ii": {
        "example": {"call": "find_order(4, [[1, 0], [2, 0], [2, 1], [3, 2]])", "expect": "[0, 1, 2, 3]"},
        "approaches": {
            "DFS post-order, reversed": {
                "idea": [
                    "Record a course when its DFS finishes, which happens after every course depending on it has been recorded.",
                    "That post-order lists dependents before their prerequisites, so reversing it gives a valid order.",
                    "Grey nodes detect cycles, as in Course Schedule.",
                ],
                "steps": [
                    "Edges go from prerequisite to course. DFS each white node, appending it to <code>post</code> when it finishes.",
                    "Return <code>post[::-1]</code>, or [] on a cycle.",
                ],
                "why": [
                    "When u finishes, everything reachable from it has already been recorded, so u ends up before all of them after the reversal.",
                    "It is O(V + E).",
                ],
                "dry": [
                    "Edges: 0 → 1, 0 → 2, 1 → 2, 2 → 3.",
                    "DFS 0 → 1 → 2 → 3: they finish in the order 3, 2, 1, and then 0 (its edge to 2 is already done).",
                    "post = [3, 2, 1, 0], reversed: <strong>[0, 1, 2, 3]</strong>.",
                ],
            },
            "Kahn's algorithm, emitting as courses become free": {
                "idea": [
                    "Kahn's queue releases courses in a valid order, so record them as they are popped.",
                    "If fewer than V courses come out, a cycle blocked the rest, and the answer is empty.",
                ],
                "steps": [
                    "Queue in-degree-0 courses; pop, append to <code>order</code>, and release dependents.",
                ],
                "why": [
                    "Each course is emitted only after all its prerequisites: O(V + E).",
                ],
                "dry": [
                    "In-degrees: 1 has 1, 2 has 2, 3 has 1. Start with [0].",
                    "Take 0: 1 becomes free, and 2 still needs 1.",
                    "Take 1: 2 becomes free. Take 2: 3 becomes free. Take 3.",
                    "The order is <strong>[0, 1, 2, 3]</strong>, the only valid order here.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ course schedule IV
    "course-schedule-iv": {
        "example": {"call": "check_if_prerequisite(3, [[1, 2], [1, 0], [2, 0]], [[1, 0], [1, 2], [0, 2]])",
                    "expect": "[True, True, False]"},
        "approaches": {
            "DFS per query": {
                "idea": [
                    "u is a prerequisite of v exactly when v can be reached from u along the edges.",
                    "Answer each query with its own search.",
                ],
                "steps": [
                    "<code>reaches(u, v)</code>: DFS from u; return <code>True</code> if v appears.",
                ],
                "why": [
                    "It is O(q·(V + E)), which is slow with many queries.",
                ],
                "dry": [
                    "Edges: 1 → 2, 1 → 0, 2 → 0.",
                    "(1, 0): 1 reaches 2 and 0, so <strong>True</strong>. (1, 2): <strong>True</strong>.",
                    "(0, 2): 0 has no outgoing edges, so <strong>False</strong>.",
                ],
            },
            "Floyd&ndash;Warshall transitive closure": {
                "idea": [
                    "Precompute <code>reach[i][j]</code> for every pair: i reaches j directly, or through some intermediate k.",
                    "After that, every query is a table lookup.",
                ],
                "steps": [
                    "Start from the direct edges.",
                    "For each k, i and j: <code>reach[i][j] |= reach[i][k] and reach[k][j]</code>.",
                ],
                "why": [
                    "It is O(V³) once, which is 10<sup>6</sup> for V = 100, then O(1) per query.",
                ],
                "dry": [
                    "Direct: reach[1][2], reach[1][0] and reach[2][0].",
                    "Going through k = 2 adds reach[1][0], which is already set.",
                    "Lookups: [<strong>True</strong>, <strong>True</strong>, <strong>False</strong>].",
                ],
            },
            "Topological order with ancestor bitsets": {
                "idea": [
                    "Process courses in topological order. A course's full prerequisite set is the union of each direct prerequisite p together with p's own set, which is already complete because p came first.",
                    "Store each set as a Python integer bitset, so a union is one <code>|</code>.",
                ],
                "steps": [
                    "Kahn's algorithm; for each edge u → v, <code>anc[v] |= anc[u] | (1 &lt;&lt; u)</code>.",
                    "A query (u, v) checks bit u of <code>anc[v]</code>.",
                ],
                "why": [
                    "It is O(V·(V + E)/w) with machine-word unions, then O(1) per query.",
                ],
                "dry": [
                    "Start: [1]. From 1: anc[2] = {1}, anc[0] = {1}; 2 becomes free.",
                    "From 2: anc[0] |= {1} | {2} = {1, 2}.",
                    "Queries: is 1 in anc[0]? yes. Is 1 in anc[2]? yes. Is 0 in anc[2]? no.",
                    "The result is <strong>[True, True, False]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ evaluate division
    "evaluate-division": {
        "example": {"call": 'calc_equation([["a", "b"], ["b", "c"]], [2.0, 3.0], [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]])',
                    "expect": "[6.0, 0.5, -1.0, 1.0, -1.0]"},
        "approaches": {
            "DFS per query, multiplying weights": {
                "idea": [
                    "Each equation a / b = k becomes two weighted edges: a → b with weight k and b → a with weight 1/k.",
                    "x / y is the product of the weights along any path from x to y.",
                ],
                "steps": [
                    "Return -1 if either variable is unknown.",
                    "DFS from x carrying the running product; return it when y is reached.",
                ],
                "why": [
                    "Consistent equations make every path give the same product. It is O(q·(V + E)).",
                ],
                "dry": [
                    "a/c: a → b (×2) → c (×3) gives <strong>6.0</strong>.",
                    "b/a: the edge weight is 1/2, so <strong>0.5</strong>.",
                    "a/e: e is unknown, so <strong>-1.0</strong>. a/a: the start is the target, so <strong>1.0</strong>. x/x: x is unknown, so <strong>-1.0</strong>.",
                ],
            },
            "Weighted union-find": {
                "idea": [
                    "Keep each variable's parent and <code>weight[v] = v / parent(v)</code>.",
                    "<code>find</code> compresses paths while multiplying weights, so afterwards <code>weight[v] = v / root</code>.",
                    "Then x / y = weight[x] / weight[y] whenever x and y share a root.",
                ],
                "steps": [
                    "Union a with b by attaching a's root under b's root with the weight that makes a / b = k.",
                    "Answer a query by checking the roots and dividing the weights.",
                ],
                "why": [
                    "Every query is nearly O(1), which pays off when there are many queries.",
                ],
                "dry": [
                    "a / b = 2: a goes under b with weight[a] = 2.",
                    "b / c = 3: b goes under c with weight[b] = 3.",
                    "a/c: find(a) compresses to the root c with weight[a] = 2·3 = 6, so 6 / 1 = <strong>6.0</strong>. b/a: 3 / 6 = <strong>0.5</strong>.",
                    "a/e and x/x involve unknown variables, so <strong>-1.0</strong>. a/a: <strong>1.0</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum height trees
    "minimum-height-trees": {
        "example": {"call": "sorted(find_min_height_trees(6, [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]]))", "expect": "[3, 4]"},
        "approaches": {
            "BFS from every node": {
                "idea": [
                    "Try every node as the root, measure the height with BFS, and keep the roots with the smallest height.",
                ],
                "steps": [
                    "<code>height(r)</code>: count BFS levels.",
                    "Return the roots that tie for the minimum.",
                ],
                "why": [
                    "It is O(n²), which is too slow for n = 2×10<sup>4</sup>.",
                ],
                "dry": [
                    "Heights: 0, 1 and 2 give 3; 3 gives 2; 4 gives 2; 5 gives 3.",
                    "The minimum is 2, so the result is <strong>[3, 4]</strong>.",
                ],
            },
            "Trim leaves layer by layer": {
                "idea": [
                    "A leaf is never a better root than its neighbour.",
                    "Remove all current leaves at once (which creates new leaves) and repeat until at most 2 nodes remain.",
                    "Those last nodes are the centre of the tree: every longest path loses one node from each end per round, so its middle survives.",
                ],
                "steps": [
                    "Collect the degree-1 nodes.",
                    "While more than 2 nodes remain: remove the leaves and collect the neighbours that become leaves.",
                ],
                "why": [
                    "It is Kahn's algorithm on an undirected tree: O(n).",
                ],
                "dry": [
                    "Leaves: 0, 1, 2 and 5. Removing them leaves 2 nodes.",
                    "Node 3 loses 0, 1 and 2, so its degree drops to 1. Node 4 loses 5, so its degree drops to 1.",
                    "The remaining nodes are <strong>[3, 4]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word ladder
    "word-ladder": {
        "example": {"call": 'ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"])', "expect": "5"},
        "approaches": {
            "Build the graph by comparing every pair": {
                "idea": [
                    "Words are nodes, with an edge between words one letter apart. The shortest ladder is a BFS shortest path.",
                    "Find the edges by comparing every pair of words.",
                ],
                "steps": [
                    "Compare every pair; connect those differing in exactly one position.",
                    "BFS from the begin word, counting words.",
                ],
                "why": [
                    "Building the graph is O(N²·L), with 12.5 million comparisons for 5000 words.",
                ],
                "dry": [
                    "Edges include hit–hot, hot–dot, hot–lot, dot–dog, lot–log, dog–cog, log–cog.",
                    "BFS: hit (1), hot (2), dot and lot (3), dog and log (4), cog (5).",
                    "The result is <strong>5</strong>.",
                ],
            },
            "BFS, generating neighbours by changing each letter": {
                "idea": [
                    "Do not build the graph. From each word, try all 26 letters at each position and keep the candidates that are in the word set.",
                    "Remove words from the set when they are enqueued; that doubles as the visited check.",
                ],
                "steps": [
                    "BFS with <code>(word, length)</code>; generate 26·L candidates per word.",
                ],
                "why": [
                    "It is O(N·26·L²), much better when N is large.",
                ],
                "dry": [
                    "hit → hot (changing 'i' to 'o').",
                    "hot → dot and lot. dot → dog. lot → log.",
                    "dog → cog. The length is <strong>5</strong>.",
                ],
            },
            "Wildcard pattern buckets, bidirectional BFS": {
                "idea": [
                    "Index each word under its L wildcard patterns (hot → *ot, h*t, ho*). Words sharing a pattern are exactly one letter apart, so neighbours come straight from the buckets.",
                    "Search from both ends at once, always expanding the smaller frontier, and stop when they meet.",
                ],
                "steps": [
                    "Build the buckets.",
                    "Alternate expansions; return the step count when a neighbour is found in the other frontier.",
                ],
                "why": [
                    "It is O(N·L²) and explores far fewer words on long ladders.",
                ],
                "dry": [
                    "Step 2: expand {hit}; the bucket h*t gives {hot}. Step 3: expand {hot}, giving {dot, lot}.",
                    "That frontier is larger than {cog}, so swap. Step 4: expand {cog}; the bucket *og gives {dog, log}.",
                    "Step 5: expand dog; the bucket do* contains dot, which is in the other frontier.",
                    "The searches meet, so the result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ network delay time
    "network-delay-time": {
        "example": {"call": "network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2)", "expect": "2"},
        "approaches": {
            "Bellman&ndash;Ford": {
                "idea": [
                    "Relax every edge: if going through u gives v a shorter distance, take it.",
                    "A shortest path has at most V - 1 edges, so V - 1 rounds of relaxing everything are enough. Stop early when a round changes nothing.",
                    "The answer is the largest shortest distance, or -1 if some node is unreachable.",
                ],
                "steps": [
                    "<code>dist[k] = 0</code>; repeat rounds of <code>dist[v] = min(dist[v], dist[u] + w)</code>.",
                ],
                "why": [
                    "It also handles negative weights. It is O(V·E).",
                ],
                "dry": [
                    "Round 1: 2 → 1 gives dist 1; 2 → 3 gives dist 1; 3 → 4 gives dist 2 (it uses the 3 just updated).",
                    "Round 2 changes nothing, so stop.",
                    "The distances are 1, 0, 1, 2, and the maximum is <strong>2</strong>.",
                ],
            },
            "Floyd&ndash;Warshall": {
                "idea": [
                    "Compute all-pairs shortest distances by allowing each node in turn as an intermediate stop.",
                ],
                "steps": [
                    "<code>d[i][j] = min(d[i][j], d[i][m] + d[m][j])</code> for each m.",
                ],
                "why": [
                    "It is wasteful for one source, but with n ≤ 100 it is 10<sup>6</sup> steps: O(V³).",
                ],
                "dry": [
                    "Directly, d[2][1] = 1 and d[2][3] = 1.",
                    "Through m = 3, d[2][4] = 1 + 1 = 2.",
                    "max(d[2][1..4]) = <strong>2</strong>.",
                ],
            },
            "Dijkstra with a min-heap": {
                "idea": [
                    "Always settle the closest node not yet settled. With non-negative weights, no later route can beat it.",
                    "Push improved distances onto the heap, and skip stale entries for nodes already settled.",
                ],
                "steps": [
                    "Pop <code>(d, u)</code>; if u is settled, skip it; otherwise record it and push its neighbours.",
                    "Return the maximum distance if every node was settled, otherwise -1.",
                ],
                "why": [
                    "It is O(E log V).",
                ],
                "dry": [
                    "Pop (0, 2): push (1, 1) and (1, 3).",
                    "Pop (1, 1): settled. Pop (1, 3): push (2, 4).",
                    "Pop (2, 4). All 4 nodes are settled; the maximum is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ path with minimum effort
    "path-minimum-effort": {
        "example": {"call": "minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]])", "expect": "2"},
        "approaches": {
            "Binary search on the effort, BFS to test it": {
                "idea": [
                    "\"Is there a path using only steps with a height difference of at most e?\" is monotonic in e, and one BFS answers it.",
                    "Binary-search the smallest e that works.",
                ],
                "steps": [
                    "<code>possible(limit)</code>: BFS using only steps within the limit.",
                    "Binary-search e over [0, max height].",
                ],
                "why": [
                    "It is O(m·n·log H).",
                ],
                "dry": [
                    "e = 4 works, for example along the top row and down the right side.",
                    "e = 2 works via the left column and bottom row: 1 → 3 → 5 → 3 → 5, every step 2.",
                    "e = 1 fails, so the result is <strong>2</strong>.",
                ],
            },
            "Union-find over edges sorted by difference": {
                "idea": [
                    "Sort every grid edge by height difference and add them cheapest first, uniting cells, until start and end are connected.",
                    "The last edge added is the answer: every path needs an edge at least that large, and these edges already connect the two corners.",
                ],
                "steps": [
                    "Build the edges with their differences; sort them.",
                    "Union in order; return the weight when <code>find(0) == find(end)</code>.",
                ],
                "why": [
                    "This is Kruskal stopped early: O(E log E).",
                ],
                "dry": [
                    "The difference-0 and difference-1 edges connect only small pieces near the top right.",
                    "Adding the difference-2 edges joins (0,0)–(1,0)–(2,0)–(2,1)–(2,2).",
                    "The start and end connect at difference <strong>2</strong>.",
                ],
            },
            "Dijkstra with max instead of sum": {
                "idea": [
                    "Run Dijkstra where a path's cost is its largest single step: moving to a neighbour costs <code>max(effort, |Δh|)</code>.",
                    "This cost never decreases along a path, so Dijkstra's argument still holds: the first time the target is popped, its effort is optimal.",
                ],
                "steps": [
                    "Heap of <code>(effort, r, c)</code>; relax when the new effort beats <code>best[a][b]</code>.",
                ],
                "why": [
                    "It is O(m·n·log(m·n)).",
                ],
                "dry": [
                    "Cells reachable with effort ≤ 1 are settled first: (0,1), (0,2), (1,2).",
                    "Effort-2 cells follow: (1,0), (2,0), (2,1), (2,2).",
                    "The target pops with effort <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ swim in rising water
    "swim-rising-water": {
        "example": {"call": "swim_in_water([[3, 2, 4], [0, 8, 1], [5, 7, 6]])", "expect": "6"},
        "approaches": {
            "Binary search on time, BFS to test it": {
                "idea": [
                    "At time t, only cells with elevation ≤ t can be used. Test whether such cells connect the corners with BFS.",
                    "That is monotonic in t, so binary-search the smallest t that works.",
                ],
                "steps": [
                    "<code>possible(t)</code>: the start must be ≤ t; BFS through cells ≤ t.",
                    "Binary search over [0, n² - 1].",
                ],
                "why": [
                    "It is O(n² log n²).",
                ],
                "dry": [
                    "t = 4: cells 3, 2, 4, 0, 1 are usable, but the corner (6) is not. Fails.",
                    "t = 6: 3 → 2 → 4 → 1 → 6 reaches the corner. Works.",
                    "t = 5: 5 is added, but the corner is still 6. Fails. The result is <strong>6</strong>.",
                ],
            },
            "Dijkstra on the maximum elevation so far": {
                "idea": [
                    "Always expand the reachable cell with the lowest elevation; the time needed so far is the highest elevation popped.",
                    "When the corner is popped, that maximum is the answer.",
                ],
                "steps": [
                    "Heap by elevation; track <code>t = max(t, h)</code>.",
                ],
                "why": [
                    "It is Prim's algorithm growing from the start and stopped at the target: O(n² log n).",
                ],
                "dry": [
                    "Pop 3 (the start), then 0, 2, 4, so t = 4. Then 1, then 5 (t = 5).",
                    "Pop 6, the corner, so t = 6.",
                    "The result is <strong>6</strong>.",
                ],
            },
            "Union-find, adding cells in order of elevation": {
                "idea": [
                    "Elevations are a permutation of 0..n²-1, so cells can be indexed directly by elevation, with no sort.",
                    "Switch cells on in order of elevation, uniting each with neighbours already on, and stop when the corners are in the same set.",
                ],
                "steps": [
                    "<code>where[h] = (r, c)</code>.",
                    "For t from 0: turn on <code>where[t]</code>, union it with lower neighbours, and check the corners.",
                ],
                "why": [
                    "It is O(n²·α).",
                ],
                "dry": [
                    "t=0..2: the cells 0, 1 and 2 turn on.",
                    "t=3: the start joins 0 and 2. t=4: 4 joins 2 and 1. t=5: 5 joins 0.",
                    "t=6: the corner joins 1, which connects it to the start. The result is <strong>6</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ cheapest flights within k stops
    "cheapest-flights-k-stops": {
        "example": {"call": "find_cheapest_price(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1)",
                    "expect": "700"},
        "approaches": {
            "Bellman&ndash;Ford, k + 1 rounds": {
                "idea": [
                    "After round i, <code>price[v]</code> is the cheapest cost to reach v using at most i flights.",
                    "Each round relaxes every flight from a <em>copy</em> of the previous round's prices, so one round never chains two flights.",
                    "k stops means k + 1 flights, so run k + 1 rounds.",
                ],
                "steps": [
                    "<code>prev = price[:]</code>; for each flight, <code>price[v] = min(price[v], prev[u] + w)</code>.",
                ],
                "why": [
                    "Without the copy, a single round could chain flights and break the stop limit.",
                    "It is O(k·E).",
                ],
                "dry": [
                    "Round 1 (one flight): price[1] = 100.",
                    "Round 2 (two flights): price[2] = 200 and price[3] = 100 + 600 = 700.",
                    "Reading only the previous round, 2 → 3 cannot use the new 200 yet, so the cheaper 400 (three flights) is correctly ignored.",
                    "The result is <strong>700</strong>.",
                ],
            },
            "BFS by number of flights, with pruning": {
                "idea": [
                    "Expand level by level, one level per flight, carrying (city, cost).",
                    "Only push a city if this cost beats the best known cost for it.",
                ],
                "steps": [
                    "Run k + 1 levels from the source.",
                ],
                "why": [
                    "It is O(k·E).",
                ],
                "dry": [
                    "Level 1: (1, 100). Level 2: (2, 200) and (3, 700).",
                    "Stop after k + 1 = 2 levels. best[3] = <strong>700</strong>.",
                ],
            },
            "Dijkstra on (city, flights used)": {
                "idea": [
                    "Plain Dijkstra on cities ignores the stop limit. Make the state (city, flights used), and it is correct again.",
                    "Pop the cheapest state; the first time the destination is popped is the answer. Skip states that exceed the limit or arrive with no fewer flights than before.",
                ],
                "steps": [
                    "Heap of <code>(cost, city, used)</code>.",
                ],
                "why": [
                    "It is O(k·E log(k·V)).",
                ],
                "dry": [
                    "Pop (0, city 0, 0 flights): push (100, 1, 1).",
                    "Pop (100, 1, 1): push (200, 2, 2) and (700, 3, 2).",
                    "Pop (200, 2, 2): 2 flights is more than the limit allows from there, so skip it.",
                    "Pop (700, 3, 2): the destination, so the result is <strong>700</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reconstruct itinerary
    "reconstruct-itinerary": {
        "example": {"call": 'find_itinerary([["JFK", "KUL"], ["JFK", "NRT"], ["NRT", "JFK"]])', "expect": '["JFK", "NRT", "JFK", "KUL"]'},
        "approaches": {
            "DFS with backtracking, smallest destination first": {
                "idea": [
                    "Try destinations in alphabetical order, using up each ticket as you go.",
                    "If a branch cannot use every ticket, give the ticket back and try the next destination.",
                    "The first complete itinerary found is the smallest.",
                ],
                "steps": [
                    "Mark a ticket used (<code>None</code>), recurse, and restore it on failure.",
                    "Stop when the route has every ticket.",
                ],
                "why": [
                    "It is usually fast, but exponential on adversarial inputs.",
                ],
                "dry": [
                    "From JFK, try KUL first: KUL has no tickets, and NRT → JFK is unused, so it is a dead end. Give the ticket back.",
                    "Try NRT: NRT → JFK → KUL uses all three tickets.",
                    "The result is <strong>[\"JFK\", \"NRT\", \"JFK\", \"KUL\"]</strong>.",
                ],
            },
            "Hierholzer's algorithm": {
                "idea": [
                    "Using every ticket once is an Eulerian path. Walk greedily, always taking the smallest ticket.",
                    "When an airport has no tickets left, it must be the end of whatever remains of the route: add it to the answer and back up.",
                    "A dead end is not a failure; it is the tail of the route, and the detours found while backing up get placed in front of it. Reverse at the end.",
                ],
                "steps": [
                    "Destinations go in reverse-sorted lists, so <code>pop()</code> gives the smallest.",
                    "Use a stack: push while tickets remain, and pop to <code>route</code> when stuck.",
                ],
                "why": [
                    "Each ticket is used once: O(E log E) for the sort.",
                ],
                "dry": [
                    "The stack [JFK] takes the smallest ticket, KUL. KUL has none, so route = [KUL].",
                    "Back at JFK, take NRT, then NRT → JFK.",
                    "JFK, NRT and JFK are all stuck, so route = [KUL, JFK, NRT, JFK].",
                    "Reversed: <strong>[\"JFK\", \"NRT\", \"JFK\", \"KUL\"]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ min cost to connect all points
    "min-cost-connect-points": {
        "example": {"call": "min_cost_connect_points([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]])", "expect": "20"},
        "approaches": {
            "Kruskal: sort all edges, union-find": {
                "idea": [
                    "This is a minimum spanning tree on the complete graph, with Manhattan distances as weights.",
                    "Kruskal: sort the edges and keep each one that joins two different components, until n - 1 are kept.",
                ],
                "steps": [
                    "Build all n(n-1)/2 edges and sort them.",
                    "Union in order, adding the weights.",
                ],
                "why": [
                    "The cheapest edge across any cut is always safe to take. It is O(n² log n).",
                ],
                "dry": [
                    "Cheapest: (2,2)–(5,2) costs 3. Then (0,0)–(2,2) costs 4 and (5,2)–(7,0) costs 4.",
                    "The 7-cost edges would close cycles, so they are skipped.",
                    "(2,2)–(3,10) costs 9. The total is 3 + 4 + 4 + 9 = <strong>20</strong>.",
                ],
            },
            "Prim with a min-heap": {
                "idea": [
                    "Grow a tree from point 0: repeatedly pop the cheapest edge to an unvisited point and add it.",
                    "Push the new point's edges to all unvisited points, and skip stale heap entries.",
                ],
                "steps": [
                    "Heap of <code>(cost, point)</code>.",
                ],
                "why": [
                    "It is O(n² log n) on a complete graph.",
                ],
                "dry": [
                    "Start at (0,0). The cheapest is (2,2) at cost 4.",
                    "From (2,2), (5,2) costs 3. From (5,2), (7,0) costs 4.",
                    "The last point (3,10) is cheapest from (2,2) at 9. The total is <strong>20</strong>.",
                ],
            },
            "Prim with a distance array (dense graphs)": {
                "idea": [
                    "On a complete graph, keep <code>dist[j]</code> = the cheapest edge from the tree to j.",
                    "Each step picks the closest unvisited point with a linear scan and updates the distances from it.",
                ],
                "steps": [
                    "Repeat n times: pick the minimum, add it, relax the others.",
                ],
                "why": [
                    "It is O(n²) with no heap and no edge list, which is optimal for dense graphs.",
                ],
                "dry": [
                    "dist from (0,0): 4, 13, 7, 7. Pick (2,2) (4).",
                    "Update: (3,10) → 9, (5,2) → 3, (7,0) → 7. Pick (5,2) (3).",
                    "Update: (7,0) → 4. Pick (7,0) (4), then (3,10) (9).",
                    "The total is <strong>20</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ alien dictionary
    "alien-dictionary": {
        "example": {"call": 'alien_order(["wrt", "wrf", "er", "ett", "rftt"])', "expect": '"wertf"'},
        "approaches": {
            "Adjacent-pair edges, DFS post-order": {
                "idea": [
                    "Only adjacent words give information, and only at their first differing letter: <code>a[i]</code> comes before <code>b[i]</code>.",
                    "If a word is followed by its own prefix, no order works.",
                    "Topologically sort the letters: emit each letter when its DFS finishes, reverse, and treat a grey hit as a cycle.",
                ],
                "steps": [
                    "Add an edge per adjacent pair.",
                    "Run a three-colour DFS; reverse the finishing order.",
                ],
                "why": [
                    "It is O(C) for C characters (at most 26 letters).",
                ],
                "dry": [
                    "Pairs: wrt/wrf gives t → f; wrf/er gives w → e; er/ett gives r → t; ett/rftt gives e → r.",
                    "That is the chain w → e → r → t → f.",
                    "DFS from w finishes f, t, r, e, w; reversed: <strong>\"wertf\"</strong>.",
                ],
            },
            "Adjacent-pair edges, Kahn's algorithm": {
                "idea": [
                    "The same edges, then repeatedly output a letter with no remaining predecessors.",
                    "If fewer letters come out than exist, the constraints contain a cycle.",
                ],
                "steps": [
                    "Count in-degrees once per distinct edge.",
                    "Queue the letters with in-degree 0 and release their successors as they are output.",
                ],
                "why": [
                    "It is iterative; swapping the queue for a heap gives the smallest order.",
                ],
                "dry": [
                    "Only w has in-degree 0.",
                    "w releases e, e releases r, r releases t, t releases f.",
                    "The result is <strong>\"wertf\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ critical and pseudo-critical edges
    "critical-pseudo-critical-edges": {
        "example": {"call": "find_critical_and_pseudo_critical_edges(5, [[0, 1, 1], [1, 2, 1], [2, 3, 2], [0, 3, 2], [0, 4, 3], [3, 4, 3], [1, 4, 6]])",
                    "expect": "[[0, 1], [2, 3, 4, 5]]"},
        "approaches": {
            "Kruskal once per edge, excluded and forced": {
                "idea": [
                    "Compute the MST weight W once.",
                    "An edge is <em>critical</em> if removing it makes the MST heavier (or impossible): rerun Kruskal without it.",
                    "Otherwise it is <em>pseudo-critical</em> if some MST still uses it: rerun Kruskal with it forced in first and check the weight is still W.",
                ],
                "steps": [
                    "Sort the edges once and reuse that order.",
                    "For each edge: <code>mst(skip=i) &gt; W</code> means critical; otherwise <code>mst(force=i) == W</code> means pseudo-critical.",
                ],
                "why": [
                    "That is two Kruskal runs per edge: O(E²·α(V)), fine for E ≤ 200.",
                ],
                "dry": [
                    "W = 1 + 1 + 2 + 3 = 7.",
                    "Without edge 0 or edge 1 (the weight-1 edges), the MST gets heavier, so both are critical.",
                    "Edges 2 and 3 (weight 2) and 4 and 5 (weight 3) can each be swapped for their twin, so forcing them still gives 7: pseudo-critical. Edge 6 forced in gives more than 7.",
                    "The result is <strong>[[0, 1], [2, 3, 4, 5]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ build a matrix with conditions
    "build-matrix-conditions": {
        "example": {"call": "build_matrix(3, [[1, 2], [2, 3]], [[3, 2], [2, 1]])", "expect": "[[0, 0, 1], [0, 2, 0], [3, 0, 0]]"},
        "approaches": {
            "Two topological sorts with DFS": {
                "idea": [
                    "Row conditions only constrain rows and column conditions only constrain columns, so the two can be solved separately.",
                    "Topologically sort 1..k under the row conditions to get each number's row, and under the column conditions to get its column.",
                    "A cycle in either set means no matrix exists.",
                ],
                "steps": [
                    "<code>topo(conds)</code>: three-colour DFS, reversed post-order.",
                    "Place each number v at <code>(row_of[v], col_of[v])</code>.",
                ],
                "why": [
                    "Each number has a distinct row and a distinct column, so they never collide. It is O(k + n).",
                ],
                "dry": [
                    "Rows: 1 above 2, and 2 above 3, give the order [1, 2, 3].",
                    "Columns: 3 left of 2, and 2 left of 1, give the order [3, 2, 1].",
                    "So 1 is at (0, 2), 2 at (1, 1), 3 at (2, 0).",
                    "The result is <strong>[[0, 0, 1], [0, 2, 0], [3, 0, 0]]</strong>.",
                ],
            },
            "Two topological sorts with Kahn's algorithm": {
                "idea": [
                    "The same plan, with Kahn's algorithm per dimension; an order shorter than k signals a cycle.",
                ],
                "steps": [
                    "<code>topo</code> returns the Kahn order, or <code>None</code>.",
                ],
                "why": [
                    "It is iterative, and both sorts share one helper.",
                ],
                "dry": [
                    "The row order is [1, 2, 3] and the column order is [3, 2, 1], both unique here.",
                    "The result is <strong>[[0, 0, 1], [0, 2, 0], [3, 0, 0]]</strong>.",
                ],
            },
        },
    },
}
