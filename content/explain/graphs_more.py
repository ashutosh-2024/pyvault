"""Write-ups for the Graphs topic, part 2: topological sort, weighted graphs, graph structure."""

EXPLAIN = {
    # ------------------------------------------------------------------ course schedule
    "course-schedule": {
        "examples": [
            {"call": "can_finish(4, [[1, 0], [2, 1], [3, 2], [1, 3]])", "expect": "False"},
            {"call": "can_finish(3, [[1, 0], [2, 0], [2, 1]])", "expect": "True"},
        ],
        "approaches": {
            "DFS with three colours": {
                "idea": [
                    "Courses are nodes and \"take b before a\" is an edge b → a. All courses can be finished exactly when this graph has <strong>no cycle</strong>.",
                    "During DFS, colour nodes white (unvisited), grey (on the current path) and black (finished, known to be cycle-free).",
                    "Reaching a grey node means the path has looped back on itself; reaching a black node is harmless and is skipped.",
                ],
                "steps": [
                    "Build <code>adj</code> with an edge <code>b → a</code> for each pair <code>[a, b]</code>.",
                    "Start every course <code>WHITE</code> in <code>color</code>.",
                    "<code>has_cycle(u)</code> colours <code>u</code> grey, then checks each neighbour <code>v</code>: grey means a cycle; white means recurse into it.",
                    "If no neighbour reports a cycle, colour <code>u</code> black and return <code>False</code>.",
                    "Run <code>has_cycle</code> from every course still white; return <code>True</code> only if none finds a cycle.",
                ],
                "why": [
                    "The grey nodes are exactly the current recursion path, so an edge into a grey node is a back edge and closes a cycle; any cycle produces such an edge when DFS first enters it.",
                    "A black node's whole reachable area has been explored without a cycle, so revisiting it cannot find one.",
                    "Each node is coloured grey once and each edge examined once: <strong>O(V + E)</strong> time, with <strong>O(V + E)</strong> space for the graph, colours and recursion stack.",
                ],
                "dry": [
                    [
                        "Edges: 0 → 1, 1 → 2, 2 → 3, 3 → 1.",
                        "has_cycle(0): 0 grey, recurse into 1; 1 grey, recurse into 2; 2 grey, recurse into 3; 3 grey.",
                        "From 3, the neighbour 1 is grey: it is still on the path 0 → 1 → 2 → 3, so this is a cycle.",
                        "<code>any</code> is true, so the result is <strong>False</strong>.",
                    ],
                    [
                        "Edges: 0 → 1, 0 → 2, 1 → 2.",
                        "has_cycle(0): 0 grey, recurse into 1; 1 grey, recurse into 2; 2 has no edges and turns black.",
                        "1 turns black. Back at 0, neighbour 2 is black, so it is skipped, not reported as a cycle.",
                        "0 turns black; courses 1 and 2 are not white any more. No cycle: <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not a single visited flag?",
                     "In example 2, node 2 is reached twice (from 1 and from 0) without any cycle. A plain flag cannot tell \"on my path\" (grey) from \"finished earlier\" (black)."],
                    ["Why is <code>has_cycle</code> called from every white node, not just node 0?",
                     "The graph may be disconnected, and a cycle in a part unreachable from 0 must still be found."],
                    ["Any risk with recursion here?",
                     "A long prerequisite chain recurses once per course, which can hit Python's default limit of about 1000. Kahn's algorithm is iterative and avoids that."],
                ],
            },
            "Kahn's algorithm (BFS on in-degrees)": {
                "idea": [
                    "A course's in-degree is the number of prerequisites it still waits for. Courses with in-degree 0 can be taken now.",
                    "Taking a course lowers each dependent's count, and any that reach 0 become available.",
                    "Courses on a cycle wait for each other forever and never reach 0, so if not every course gets taken there is a cycle.",
                ],
                "steps": [
                    "Build <code>adj</code> (b → a) and <code>indeg</code> by counting incoming edges.",
                    "Queue every course with <code>indeg[u] == 0</code>.",
                    "Pop <code>u</code> and add 1 to <code>taken</code>.",
                    "For each dependent <code>v</code>, decrement <code>indeg[v]</code>; when it hits 0, append <code>v</code> to the queue.",
                    "Return <code>taken == num_courses</code>.",
                ],
                "why": [
                    "A course is popped only after all its prerequisites have been popped, so the pop order is a valid schedule.",
                    "In a cycle, each member has a prerequisite inside the cycle that is never popped, so none of them is ever taken and <code>taken</code> falls short.",
                    "Each course is queued once and each edge decremented once: <strong>O(V + E)</strong> time and <strong>O(V + E)</strong> space.",
                ],
                "dry": [
                    [
                        "indeg = [0, 2, 1, 1]: course 1 waits for 0 and 3. queue = [0].",
                        "Pop 0, taken=1. indeg[1] drops to 1, still blocked by 3.",
                        "The queue is empty. Courses 1, 2 and 3 block each other.",
                        "taken = 1 ≠ 4, so the result is <strong>False</strong>.",
                    ],
                    [
                        "indeg = [0, 1, 2]. queue = [0].",
                        "Pop 0, taken=1: indeg[1] → 0 (queue it), indeg[2] → 1.",
                        "Pop 1, taken=2: indeg[2] → 0, queue it. Pop 2, taken=3.",
                        "taken = 3 = num_courses: <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why queue a course only when its in-degree reaches exactly 0?",
                     "Each edge is decremented once, so the count passes through 0 exactly once and the course is queued exactly once."],
                    ["Does the queue order matter?",
                     "Not for the yes/no answer. A stack would also work; any order that only takes free courses gives a valid schedule."],
                    ["What if a pair lists the same prerequisite twice?",
                     "Both the edge and the in-degree are counted twice, so the two decrements cancel the two increments and the result is still correct."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ course schedule II
    "course-schedule-ii": {
        "examples": [
            {"call": "find_order(4, [[1, 0], [2, 0], [2, 1], [3, 2]])", "expect": "[0, 1, 2, 3]"},
            {"call": "find_order(2, [[0, 1], [1, 0]])", "expect": "[]"},
        ],
        "approaches": {
            "DFS post-order, reversed": {
                "idea": [
                    "A course finishes its DFS only after every course that depends on it has finished, so the finish order (post-order) lists dependents before prerequisites.",
                    "Reversing the post-order therefore puts every prerequisite before the courses that need it.",
                    "The same grey/black colouring as Course Schedule detects a cycle, in which case no order exists.",
                ],
                "steps": [
                    "Build <code>adj</code> with edges <code>b → a</code>; <code>color</code> is 0 (white), 1 (grey) or 2 (black).",
                    "<code>dfs(u)</code> colours <code>u</code> grey and visits each neighbour; a grey neighbour, or a failing recursive call, returns <code>False</code>.",
                    "After all neighbours, colour <code>u</code> black and append it to <code>post</code>.",
                    "Call <code>dfs</code> from every white course; return <code>[]</code> if any call fails.",
                    "Return <code>post[::-1]</code>.",
                ],
                "why": [
                    "For an edge u → v, either v is already black (appended before u), or v is visited inside u's call and finishes first. Either way u comes after v in <code>post</code>, so before it in the reversal.",
                    "A grey neighbour means a cycle, and then no order can exist, so returning <code>[]</code> is correct.",
                    "Each node and edge is processed once: <strong>O(V + E)</strong> time and <strong>O(V + E)</strong> space.",
                ],
                "dry": [
                    [
                        "Edges: 0 → 1, 0 → 2, 1 → 2, 2 → 3.",
                        "dfs(0) → dfs(1) → dfs(2) → dfs(3). Course 3 has no edges: post = [3].",
                        "Unwinding: post = [3, 2], then [3, 2, 1].",
                        "Back in 0, neighbour 2 is already black, so it is skipped. post = [3, 2, 1, 0].",
                        "Reversed: <strong>[0, 1, 2, 3]</strong>.",
                    ],
                    [
                        "Edges: 1 → 0 and 0 → 1.",
                        "dfs(0): 0 grey, visit 1. dfs(1): 1 grey, visit 0, which is grey.",
                        "dfs(1) returns False, so dfs(0) returns False.",
                        "A cycle means no valid order: <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why append to <code>post</code> after the neighbours and not before?",
                     "Appending before (pre-order) does not guarantee prerequisites come first once reversed; only finish order has the property that every dependent finishes earlier."],
                    ["Can I avoid reversing?",
                     "Yes, by building the graph with edges a → b (course to its prerequisite). Then post-order itself lists prerequisites first."],
                    ["Is the answer unique?",
                     "Often not. Any topological order is accepted; example 1 happens to have exactly one."],
                ],
            },
            "Kahn's algorithm, emitting as courses become free": {
                "idea": [
                    "Kahn's algorithm takes courses in an order where every prerequisite comes first, which is exactly the required answer.",
                    "Record each course as it is popped. If fewer than <code>num_courses</code> are recorded, a cycle blocked the rest.",
                ],
                "steps": [
                    "Build <code>adj</code> and <code>indeg</code> from the prerequisite pairs.",
                    "Queue all courses with in-degree 0.",
                    "Pop <code>u</code>, append it to <code>order</code>, and decrement each dependent's in-degree.",
                    "Queue any dependent whose in-degree reaches 0.",
                    "Return <code>order</code> if it has every course, otherwise <code>[]</code>.",
                ],
                "why": [
                    "A course enters the queue only when all its prerequisites have been appended, so <code>order</code> is valid.",
                    "Courses on or behind a cycle never reach in-degree 0, so a short <code>order</code> means no valid order exists.",
                    "Each course and edge is handled once: <strong>O(V + E)</strong> time and <strong>O(V + E)</strong> space.",
                ],
                "dry": [
                    [
                        "indeg: course 1 = 1, course 2 = 2, course 3 = 1. queue = [0].",
                        "Pop 0, order = [0]: indeg[1] → 0 (queue it), indeg[2] → 1.",
                        "Pop 1, order = [0, 1]: indeg[2] → 0, queue it.",
                        "Pop 2, order = [0, 1, 2]: indeg[3] → 0. Pop 3.",
                        "All 4 courses are taken: <strong>[0, 1, 2, 3]</strong>.",
                    ],
                    [
                        "indeg = [1, 1]: each course waits for the other.",
                        "No course has in-degree 0, so the queue starts empty.",
                        "order = [] has length 0 ≠ 2: <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>len(order) == num_courses</code> at the end?",
                     "When there is a cycle the loop still ends normally, just early. The length is the only signal that some courses were never freed."],
                    ["Do courses with no prerequisites and no dependents appear?",
                     "Yes. Their in-degree is 0, so they are queued at the start and emitted."],
                    ["DFS or Kahn for this problem?",
                     "Both are O(V + E). Kahn is iterative and builds the order directly; DFS needs a reversal and can hit the recursion limit."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ course schedule IV
    "course-schedule-iv": {
        "examples": [
            {"call": "check_if_prerequisite(3, [[1, 2], [1, 0], [2, 0]], [[1, 0], [1, 2], [0, 2]])", "expect": "[True, True, False]"},
            {"call": "check_if_prerequisite(3, [[0, 1], [1, 2]], [[0, 2], [2, 0]])", "expect": "[True, False]"},
        ],
        "approaches": {
            "DFS per query": {
                "idea": [
                    "u is a prerequisite of v when v can be reached from u along prerequisite edges, directly or through a chain.",
                    "Answer each query independently with a fresh search from u.",
                ],
                "steps": [
                    "Build <code>adj</code> with an edge <code>a → b</code> for each pair <code>[a, b]</code> (a must come before b).",
                    "<code>reaches(u, v)</code> runs an iterative DFS from <code>u</code> with <code>seen</code> and <code>stack</code>.",
                    "When a popped node <code>x</code> equals <code>v</code>, return <code>True</code>.",
                    "Push each unseen neighbour <code>y</code>; if the stack empties, return <code>False</code>.",
                    "Map <code>reaches</code> over all queries.",
                ],
                "why": [
                    "Prerequisite is transitive, so \"u before v\" is exactly reachability from u to v, which a DFS decides.",
                    "Each query may explore the whole graph: <strong>O(q · (V + E))</strong> time.",
                    "The graph plus one query's <code>seen</code> and stack: <strong>O(V + E)</strong> space.",
                ],
                "dry": [
                    [
                        "adj: 1 → [2, 0], 2 → [0].",
                        "(1, 0): pop 1, push 2 and 0. Pop 0: it is the target → True.",
                        "(1, 2): pop 1, push 2 and 0. Pop 0 (no edges), pop 2 → True.",
                        "(0, 2): pop 0, which has no edges. Stack empty → False.",
                        "The result is <strong>[True, True, False]</strong>.",
                    ],
                    [
                        "adj: 0 → [1], 1 → [2].",
                        "(0, 2): pop 0, push 1; pop 1, push 2; pop 2 → True, through the chain 0 → 1 → 2.",
                        "(2, 0): pop 2, which has no edges → False.",
                        "The result is <strong>[True, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why test <code>x == v</code> when popping rather than when pushing?",
                     "Either works. Testing on pop also handles <code>u == v</code> naturally, though queries never ask that."],
                    ["Does the edge direction matter?",
                     "Yes. Searching from u needs edges pointing from prerequisite to dependent, a → b; reversed edges would answer the opposite question."],
                    ["When is this approach fine?",
                     "When there are few queries. With many queries, precomputing all reachability once (the other two approaches) is cheaper."],
                ],
            },
            "Floyd&ndash;Warshall transitive closure": {
                "idea": [
                    "Precompute <code>reach[i][j]</code> for every pair, then each query is a table lookup.",
                    "Floyd–Warshall builds it by allowing intermediate courses one at a time: i reaches j through k if i reaches k and k reaches j.",
                ],
                "steps": [
                    "Create an n × n table <code>reach</code> and set <code>reach[a][b] = True</code> for each direct pair.",
                    "For each intermediate <code>k</code>, for each <code>i</code> with <code>reach[i][k]</code>:",
                    "OR row <code>k</code> into row <code>i</code>: every j reachable from k is now reachable from i.",
                    "Answer each query as <code>reach[u][v]</code>.",
                ],
                "why": [
                    "After round k, <code>reach[i][j]</code> is true exactly when a path from i to j exists using only intermediates 0..k; after the last round, any path counts.",
                    "Three nested loops over n: <strong>O(V³ + q)</strong> time. Skipping rows with <code>reach[i][k]</code> false saves work but not the worst case.",
                    "The table is <strong>O(V²)</strong> space.",
                ],
                "dry": [
                    [
                        "Direct: reach[1][2], reach[1][0], reach[2][0].",
                        "k=0: course 0 reaches nothing, so no row changes. k=1: no course reaches 1.",
                        "k=2: row 1 has reach[1][2]; ORing row 2 sets reach[1][0], already true.",
                        "Lookups: reach[1][0]=T, reach[1][2]=T, reach[0][2]=F → <strong>[True, True, False]</strong>.",
                    ],
                    [
                        "Direct: reach[0][1], reach[1][2].",
                        "k=0: nothing reaches 0. k=1: row 0 has reach[0][1], so OR in row 1 → reach[0][2] = True.",
                        "k=2: row 2 is empty, no changes.",
                        "Lookups: reach[0][2]=T, reach[2][0]=F → <strong>[True, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>k</code> be the outermost loop?",
                     "Round k assumes all paths through intermediates 0..k−1 are already recorded. Putting k inside breaks that order and can miss longer chains."],
                    ["What are <code>row_k</code> and <code>row_i</code> for?",
                     "They cache the two row lists so the inner loop avoids repeated double indexing; the logic is unchanged."],
                    ["When is O(V³) acceptable?",
                     "This problem has n ≤ 100, so 10<sup>6</sup> steps is fine, and it answers up to 10<sup>4</sup> queries in O(1) each."],
                ],
            },
            "Topological order with ancestor bitsets": {
                "idea": [
                    "Store, for each course v, the set of all its prerequisites as a bitmask <code>anc[v]</code>: bit u is set when u must come before v.",
                    "Process courses in topological order, so a course's set is complete before it is passed on: each child inherits the parent's set plus the parent itself.",
                ],
                "steps": [
                    "Build <code>adj</code> (a → b) and <code>indeg</code>.",
                    "Start with <code>anc = [0] * n</code> and queue the courses with in-degree 0.",
                    "Pop <code>u</code>; for each <code>v</code> in <code>adj[u]</code>, set <code>anc[v] |= anc[u] | (1 &lt;&lt; u)</code>.",
                    "Decrement <code>indeg[v]</code> and queue it at 0, as in Kahn's algorithm.",
                    "Answer each query with bit u of <code>anc[v]</code>: <code>anc[v] &gt;&gt; u &amp; 1</code>.",
                ],
                "why": [
                    "When <code>u</code> is popped, all of its own parents were popped earlier, so <code>anc[u]</code> is final before it is copied into children.",
                    "Each edge does one OR of n-bit integers, costing about n / w machine words: <strong>O(V · (V + E) / w + q)</strong> time.",
                    "n masks of n bits: <strong>O(V² / w)</strong> space.",
                ],
                "dry": [
                    [
                        "adj: 1 → [2, 0], 2 → [0]. indeg = [2, 0, 1]. queue = [1].",
                        "Pop 1: anc[2] = 0b010, indeg[2] → 0 (queue it); anc[0] = 0b010, indeg[0] → 1.",
                        "Pop 2: anc[0] |= anc[2] | 0b100 → 0b110. indeg[0] → 0. Pop 0: no edges.",
                        "(1,0): bit 1 of 0b110 → T. (1,2): bit 1 of 0b010 → T. (0,2): bit 0 of 0b010 → F.",
                        "The result is <strong>[True, True, False]</strong>.",
                    ],
                    [
                        "adj: 0 → [1], 1 → [2]. queue = [0].",
                        "Pop 0: anc[1] = 0b001. Pop 1: anc[2] = 0b001 | 0b010 = 0b011.",
                        "(0,2): bit 0 of 0b011 → T. (2,0): anc[0] = 0 → F.",
                        "The result is <strong>[True, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>anc[v] &gt;&gt; u &amp; 1</code> mean bit u?",
                     "In Python <code>&gt;&gt;</code> binds tighter than <code>&amp;</code>, so it shifts bit u down to position 0 and then masks it."],
                    ["Why use <code>|=</code> instead of <code>=</code>?",
                     "A course can have several parents; each contributes its own ancestors, and the sets must be combined, not overwritten."],
                    ["What is w in the complexity?",
                     "The machine word size (64). Python's big integers OR 64 bits at a time, so a whole row of n flags is merged in about n / 64 steps."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ evaluate division
    "evaluate-division": {
        "examples": [
            {"call": "calc_equation([[\"a\", \"b\"], [\"b\", \"c\"]], [2.0, 3.0], [[\"a\", \"c\"], [\"b\", \"a\"], [\"a\", \"e\"], [\"a\", \"a\"], [\"x\", \"x\"]])",
             "expect": "[6.0, 0.5, -1.0, 1.0, -1.0]"},
            {"call": "calc_equation([[\"a\", \"b\"], [\"c\", \"d\"]], [1.0, 1.0], [[\"a\", \"c\"], [\"b\", \"a\"]])",
             "expect": "[-1.0, 1.0]"},
        ],
        "approaches": {
            "DFS per query, multiplying weights": {
                "idea": [
                    "Each equation a / b = k is a weighted edge a → b with weight k, plus b → a with weight 1 / k.",
                    "x / y is the product of the weights along any path from x to y, because the intermediate variables cancel: (x / m) · (m / y) = x / y.",
                ],
                "steps": [
                    "Build <code>graph[a][b] = k</code> and <code>graph[b][a] = 1 / k</code> for every equation.",
                    "<code>solve(x, y)</code>: if either variable is unknown, return <code>-1.0</code>.",
                    "Run a DFS from <code>x</code> whose stack holds <code>(node, prod)</code>, starting at <code>(x, 1.0)</code>.",
                    "When <code>node == y</code>, return <code>prod</code>; otherwise push unseen neighbours with <code>prod * w</code>.",
                    "If the stack empties, the variables are not connected: return <code>-1.0</code>.",
                ],
                "why": [
                    "The equations are consistent, so every path from x to y gives the same product, and the first one found is correct.",
                    "Each query may traverse the whole graph: <strong>O(q · (V + E))</strong> time.",
                    "The graph plus one query's stack and <code>seen</code>: <strong>O(V + E)</strong> space.",
                ],
                "dry": [
                    [
                        "graph: a → {b: 2}, b → {a: 0.5, c: 3}, c → {b: 1/3}.",
                        "(a, c): pop (a, 1), push (b, 2); pop b, push (c, 6); pop c → 6.0.",
                        "(b, a): pop b, push (a, 0.5) and (c, 3). Pop c first (LIFO), then (a, 0.5) → 0.5.",
                        "(a, e): e unknown → −1.0. (a, a): the first pop is a itself → 1.0. (x, x): x unknown → −1.0.",
                        "The result is <strong>[6.0, 0.5, -1.0, 1.0, -1.0]</strong>.",
                    ],
                    [
                        "graph: a ↔ b and c ↔ d, all weights 1.0.",
                        "(a, c): pop a, push b; pop b, whose only neighbour a is seen. Stack empty → −1.0.",
                        "(b, a): pop b, push (a, 1.0); pop a → 1.0.",
                        "The result is <strong>[-1.0, 1.0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>x / x</code> equal to −1.0 when x is unknown?",
                     "The problem defines answers only for variables that appear in equations. Nothing is known about x, so its query is undefined."],
                    ["Why do I need the reverse edge with weight 1 / k?",
                     "Queries can go either way. Without b → a, the query b / a in example 1 would find no path."],
                    ["Is the first path found always right, even with several paths?",
                     "Yes, because the input is guaranteed consistent: all paths between two variables multiply to the same value."],
                ],
            },
            "Weighted union-find": {
                "idea": [
                    "Group connected variables in a union-find, and store with each variable <code>weight[x]</code> = x / root.",
                    "Two variables in the same set have x / y = (x / root) / (y / root) = <code>weight[x] / weight[y]</code>; different sets mean −1.0.",
                ],
                "steps": [
                    "Add unseen variables with <code>parent[v] = v</code> and <code>weight[v] = 1.0</code>.",
                    "<code>find(x)</code> recursively finds the root, then multiplies <code>weight[x]</code> by the old parent's weight and points <code>x</code> straight at the root.",
                    "For each equation a / b = k with roots <code>ra ≠ rb</code>, set <code>parent[ra] = rb</code> and <code>weight[ra] = k * weight[b] / weight[a]</code>.",
                    "For a query, return −1.0 if a variable is unknown or the roots differ; otherwise <code>weight[x] / weight[y]</code>.",
                ],
                "why": [
                    "After compression, <code>weight[x]</code> = x / parent · parent / root = x / root, so the invariant holds.",
                    "Setting ra / rb = k · (b / rb) / (a / ra) makes a / rb = (a / ra) · (ra / rb) = k · b / rb, which is exactly a / b = k.",
                    "Each find is near constant amortised: <strong>O((E + q) · α)</strong> time and <strong>O(V)</strong> space for the two maps.",
                ],
                "dry": [
                    [
                        "a / b = 2: parent[a] = b, weight[a] = 2. b / c = 3: parent[b] = c, weight[b] = 3.",
                        "(a, c): find(a) compresses a under c with weight 2 · 3 = 6. find(c) = c, weight 1 → 6.0.",
                        "(b, a): same root c. weight[b] / weight[a] = 3 / 6 = 0.5.",
                        "(a, e): e unknown → −1.0. (a, a): 6 / 6 = 1.0. (x, x): unknown → −1.0.",
                        "The result is <strong>[6.0, 0.5, -1.0, 1.0, -1.0]</strong>.",
                    ],
                    [
                        "a / b = 1: parent[a] = b. c / d = 1: parent[c] = d. Both weights are 1.0.",
                        "(a, c): find(a) = b, find(c) = d, different sets → −1.0.",
                        "(b, a): both have root b. weight[b] / weight[a] = 1 / 1 = 1.0.",
                        "The result is <strong>[-1.0, 1.0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>weight[x] *= weight[parent[x]]</code> done after the recursive call?",
                     "The recursive call first makes the parent's weight relative to the root. Only then does multiplying give x / root."],
                    ["Where does <code>k * weight[b] / weight[a]</code> come from?",
                     "It is the value ra / rb that makes a / b come out as k, given a / ra = weight[a] and b / rb = weight[b]."],
                    ["Why prefer this over DFS per query?",
                     "With many queries each one costs a near-constant find instead of a full traversal."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum height trees
    "minimum-height-trees": {
        "examples": [
            {"call": "sorted(find_min_height_trees(6, [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]]))", "expect": "[3, 4]"},
            {"call": "sorted(find_min_height_trees(4, [[1, 0], [1, 2], [1, 3]]))", "expect": "[1]"},
        ],
        "approaches": {
            "BFS from every node": {
                "idea": [
                    "The height of the tree rooted at r is the number of BFS layers from r, minus one.",
                    "Compute it for every possible root and keep the roots with the smallest height.",
                ],
                "steps": [
                    "Build an undirected adjacency list <code>adj</code>.",
                    "<code>height(root)</code> runs a layer-by-layer BFS: <code>h</code> starts at −1 and increases once per non-empty <code>frontier</code>.",
                    "Each layer collects unseen neighbours into <code>nxt</code>, which becomes the next frontier.",
                    "Compute <code>hs</code> for every root and <code>best = min(hs)</code>.",
                    "Return every <code>r</code> with <code>hs[r] == best</code>.",
                ],
                "why": [
                    "BFS from r reaches nodes in order of distance, so the number of layers is the longest root-to-leaf distance, which is the height.",
                    "Each BFS is O(n) in a tree, and there are n of them: <strong>O(n²)</strong> time.",
                    "The adjacency list, one BFS's <code>seen</code> and <code>hs</code>: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Edges: 3 joins 0, 1, 2, 4; 4 joins 5.",
                        "height(0): layers {0}, {3}, {1, 2, 4}, {5} → 3. Likewise 1, 2 and 5 give 3.",
                        "height(3): {3}, {0, 1, 2, 4}, {5} → 2. height(4): {4}, {3, 5}, {0, 1, 2} → 2.",
                        "hs = [3, 3, 3, 2, 2, 3], best = 2 → <strong>[3, 4]</strong>.",
                    ],
                    [
                        "A star with centre 1.",
                        "height(1): {1}, {0, 2, 3} → 1.",
                        "height(0), height(2), height(3): leaf, centre, other leaves → 2 each.",
                        "hs = [2, 1, 2, 2] → <strong>[1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>h</code> start at −1?",
                     "The first loop iteration processes the root's own layer, which has height 0. Starting at −1 makes that first increment land on 0."],
                    ["Why can there be two answers?",
                     "When the longest path has an odd number of nodes there is one middle node; when it has an even number, two neighbouring middles tie, as with 3 and 4 in example 1."],
                    ["Is this fast enough?",
                     "For n up to 2·10<sup>4</sup> it is about 4·10<sup>8</sup> steps, too slow in Python. Leaf trimming does it in O(n)."],
                ],
            },
            "Trim leaves layer by layer": {
                "idea": [
                    "The best roots are the middle of the tree's longest path. Removing all current leaves shortens every longest path by one at each end and keeps the same middle.",
                    "Repeat until at most two nodes remain: those are the centres.",
                ],
                "steps": [
                    "If <code>n &lt;= 2</code>, every node is a centre: return <code>list(range(n))</code>.",
                    "Build <code>adj</code> as sets and collect the initial <code>leaves</code> (degree 1).",
                    "While <code>remaining &gt; 2</code>, subtract the leaf count from <code>remaining</code>.",
                    "For each leaf, pop its only neighbour <code>nb</code> and remove the leaf from <code>adj[nb]</code>; if <code>nb</code> now has degree 1, it joins <code>nxt</code>.",
                    "Set <code>leaves = nxt</code>. When the loop ends, return <code>sorted(leaves)</code>.",
                ],
                "why": [
                    "Trimming a layer of leaves lowers every node's height by exactly one, so the nodes with minimum height are unchanged; repeating converges on the centres.",
                    "Each node is removed once and each edge deleted once: <strong>O(n)</strong> time.",
                    "The adjacency sets and leaf lists take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Initial leaves: [0, 1, 2, 5]; remaining = 6.",
                        "Round 1: remaining = 2. Removing 0, 1, 2 leaves 3 with neighbour {4}, so 3 becomes a leaf; removing 5 leaves 4 with {3}, so 4 does too.",
                        "leaves = [3, 4]; remaining = 2 stops the loop.",
                        "The result is <strong>[3, 4]</strong>.",
                    ],
                    [
                        "Initial leaves: [0, 2, 3]; remaining = 4.",
                        "Round 1: remaining = 1. Removing 0 leaves adj[1] = {2, 3}; removing 2 leaves {3}, so 1 joins nxt.",
                        "Removing 3 leaves adj[1] empty (degree 0), so 1 is not added a second time.",
                        "leaves = [1]; remaining = 1 stops the loop: <strong>[1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why stop at <code>remaining &gt; 2</code> rather than 1?",
                     "A tree has one or two centres. With two left they are neighbours, and trimming them both as leaves would leave nothing."],
                    ["Why check <code>len(adj[nb]) == 1</code> right after each removal?",
                     "A node becomes a leaf the moment its degree drops to 1, and it should be added once. In example 2, node 1 later drops to 0, which <code>== 1</code> correctly ignores."],
                    ["Why the special case for n ≤ 2?",
                     "With n = 1 there are no edges and no leaves, so the loop logic does not apply; with n = 2, both nodes are centres."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word ladder
    "word-ladder": {
        "examples": [
            {"call": "ladder_length(\"hit\", \"cog\", [\"hot\", \"dot\", \"dog\", \"lot\", \"log\", \"cog\"])", "expect": "5"},
            {"call": "ladder_length(\"hot\", \"dog\", [\"hot\", \"dog\"])", "expect": "0"},
        ],
        "approaches": {
            "Build the graph by comparing every pair": {
                "idea": [
                    "Words are nodes, and two words are linked when they differ in exactly one position. The answer is the shortest path length, counted in words.",
                    "Shortest path in an unweighted graph is <strong>BFS</strong>. This version builds every edge first by comparing all pairs of words.",
                ],
                "steps": [
                    "Make <code>words</code>: <code>begin</code> plus the list, de-duplicated in order. If <code>end</code> is missing, return 0.",
                    "For every pair <code>i &lt; j</code>, count differing letters with <code>zip</code>; exactly 1 means add an edge both ways in <code>adj</code>.",
                    "BFS from <code>(begin, 1)</code>, where the number is how many words the sequence has so far.",
                    "When the popped word is <code>end</code>, return its count <code>d</code>.",
                    "Push unseen neighbours with <code>d + 1</code>; if the queue empties, return 0.",
                ],
                "why": [
                    "BFS pops words in order of distance from <code>begin</code>, so the first time <code>end</code> is popped its count is the shortest.",
                    "N words give N²/2 comparisons of length L: <strong>O(N² · L)</strong> time.",
                    "In the worst case every pair is an edge: <strong>O(N²)</strong> space for <code>adj</code>.",
                ],
                "dry": [
                    [
                        "Edges: hit–hot, hot–dot, hot–lot, dot–dog, dot–lot, dog–log, dog–cog, lot–log, log–cog.",
                        "Pop (hit, 1), push hot. Pop (hot, 2), push dot and lot.",
                        "Pop (dot, 3), push dog. Pop (lot, 3), push log.",
                        "Pop (dog, 4), push cog. Pop (log, 4): cog already seen.",
                        "Pop (cog, 5): it is the target, so the answer is <strong>5</strong>.",
                    ],
                    [
                        "words = [hot, dog]; end is present.",
                        "hot and dog differ in two positions (h/d and t/g), so there is no edge.",
                        "Pop (hot, 1): no neighbours. The queue is empty.",
                        "dog is unreachable, so the answer is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why count words instead of moves?",
                     "The problem defines the length as the number of words in the sequence, so <code>begin</code> alone already has length 1."],
                    ["Why <code>dict.fromkeys</code>?",
                     "It removes duplicates (begin may also be in the list) while keeping order, so no word becomes two nodes."],
                    ["When does pair comparison beat letter generation?",
                     "When words are long and the list is short; generating 26·L candidates per word then costs more than comparing a few pairs."],
                ],
            },
            "BFS, generating neighbours by changing each letter": {
                "idea": [
                    "Instead of comparing word pairs, generate every possible one-letter change of the current word and keep those in the dictionary.",
                    "Removing a word from the set when it is queued doubles as the visited mark, so each word is queued at most once.",
                ],
                "steps": [
                    "Put the list in a set <code>words</code>; if <code>end</code> is not in it, return 0.",
                    "Start the queue with <code>(begin, 1)</code> and discard <code>begin</code> from <code>words</code>.",
                    "Pop <code>(w, d)</code>; if <code>w == end</code>, return <code>d</code>.",
                    "For each position <code>i</code> and letter <code>ch</code>, build <code>nxt</code>; if it is in <code>words</code>, remove it and queue <code>(nxt, d + 1)</code>.",
                    "If the queue empties, return 0.",
                ],
                "why": [
                    "It is still BFS over the same graph, only the neighbours are found differently, so the first pop of <code>end</code> is the shortest length.",
                    "Each of the N words is popped once and makes 26 · L candidates, each costing O(L) to build and hash: <strong>O(N · L² · 26)</strong> time.",
                    "The set and the queue hold up to N words of length L: <strong>O(N · L)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop (hit, 1): changing position 1 gives hot. Remove and queue it.",
                        "Pop (hot, 2): position 0 gives dot, then lot.",
                        "Pop (dot, 3): position 2 gives dog. Pop (lot, 3): position 2 gives log.",
                        "Pop (dog, 4): position 0 gives cog. Pop (log, 4): cog is already removed.",
                        "Pop (cog, 5): the answer is <strong>5</strong>.",
                    ],
                    [
                        "words = {dog} after discarding hot.",
                        "Pop (hot, 1): none of the 78 one-letter changes is dog.",
                        "The queue is empty, so the answer is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why remove a word when it is queued, not when it is popped?",
                     "Removing at queue time stops two words at the same level from queuing the same neighbour twice."],
                    ["Why discard <code>begin</code> from the set?",
                     "If begin is in the list, a neighbour could change back to it and queue it again; discarding marks it visited."],
                    ["Why L² and not L in the time bound?",
                     "Each candidate is a new string of length L built by slicing, and hashing it is O(L) too, for each of the 26 · L candidates."],
                ],
            },
            "Wildcard pattern buckets, bidirectional BFS": {
                "idea": [
                    "Words that differ only in position i share the pattern with a <code>*</code> there (hot and dot both match <code>*ot</code>), so buckets keyed by pattern list neighbours directly.",
                    "Search from both ends at once and always expand the <strong>smaller</strong> frontier; the two searches meet in the middle and explore far fewer words.",
                ],
                "steps": [
                    "Return 0 if <code>end</code> is missing. Put every word (and <code>begin</code>) into the <code>buckets</code> of its L patterns.",
                    "Set <code>front = {begin}</code>, <code>back = {end}</code>, <code>seen = {begin, end}</code> and <code>steps = 1</code>.",
                    "Each round, swap so <code>front</code> is the smaller side, then add 1 to <code>steps</code>.",
                    "For each word in <code>front</code> and each of its patterns, scan the bucket: a word in <code>back</code> means the searches meet, so return <code>steps</code>.",
                    "Otherwise collect unseen words into <code>nxt</code>; it becomes <code>front</code>. If a side empties, return 0.",
                ],
                "why": [
                    "Each round extends one side by one layer, so when a neighbour lies in the other frontier the full path has exactly <code>steps</code> words, and no shorter meeting was possible earlier.",
                    "Building buckets costs O(N · L²); each word is expanded at most once over L patterns: <strong>O(N · L²)</strong> time.",
                    "The buckets store each word under L keys of length L: <strong>O(N · L²)</strong> space.",
                ],
                "dry": [
                    [
                        "front {hit}, back {cog}. Round 1: steps=2; pattern h*t gives hot → front {hot}.",
                        "Round 2: steps=3; *ot gives dot and lot → front {dot, lot}.",
                        "Round 3: front is larger, so swap: front {cog}, back {dot, lot}. steps=4; *og gives dog and log.",
                        "Round 4: sizes tie, no swap. steps=5; a bucket like <code>do*</code> (dot) or <code>lo*</code> (lot) holds a word in back.",
                        "The searches meet: the answer is <strong>5</strong>.",
                    ],
                    [
                        "front {hot}, back {dog}. Round 1: steps=2.",
                        "hot's buckets *ot, h*t, ho* contain only hot itself, which is seen and not in back.",
                        "nxt is empty, so front becomes empty and the loop stops.",
                        "The answer is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why always expand the smaller frontier?",
                     "Work grows with frontier size. Expanding the smaller side keeps both frontiers small, which is where the speed-up over one-sided BFS comes from."],
                    ["Why check <code>nb in back</code> before <code>nb in seen</code>?",
                     "Words in back are also in seen. Checking seen first would skip them and the meeting would never be detected."],
                    ["Why is <code>steps</code> incremented before the scan?",
                     "Any meeting found in this round adds one more word to the path, so the count must already include it when it is returned."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ network delay time
    "network-delay-time": {
        "examples": [
            {"call": "network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2)", "expect": "2"},
            {"call": "network_delay_time([[1, 2, 4], [1, 3, 1], [3, 2, 1]], 3, 1)", "expect": "2"},
        ],
        "approaches": {
            "Bellman&ndash;Ford": {
                "idea": [
                    "The signal reaches each node at its shortest-path distance from k, so the answer is the largest shortest distance (or −1 if some node is unreachable).",
                    "Bellman–Ford finds all distances by repeatedly <strong>relaxing</strong> every edge: if going through u is shorter, update v.",
                ],
                "steps": [
                    "Set <code>dist</code> to infinity for nodes 1..n, and <code>dist[k] = 0</code>.",
                    "Repeat up to n − 1 rounds: for each edge <code>(u, v, w)</code>, if <code>dist[u] + w &lt; dist[v]</code>, update it and set <code>changed</code>.",
                    "If a whole round changes nothing, stop early.",
                    "Take <code>best = max(dist[1:])</code> (index 0 is unused).",
                    "Return −1 if <code>best</code> is infinite, otherwise <code>best</code>.",
                ],
                "why": [
                    "A shortest path uses at most n − 1 edges, and after round i every path with up to i edges has been fully relaxed, so n − 1 rounds suffice.",
                    "Each round scans all E edges: <strong>O(V · E)</strong> time in the worst case.",
                    "Only the <code>dist</code> array is kept: <strong>O(V)</strong> space.",
                ],
                "dry": [
                    [
                        "dist[2] = 0, the rest ∞.",
                        "Round 1: 2→1 sets dist[1]=1, 2→3 sets dist[3]=1, 3→4 sets dist[4]=2.",
                        "Round 2: no edge improves anything, so the loop breaks.",
                        "dist[1:] = [1, 0, 1, 2], so the answer is <strong>2</strong>.",
                    ],
                    [
                        "dist[1] = 0.",
                        "Round 1: 1→2 sets dist[2]=4, 1→3 sets dist[3]=1, then 3→2 improves dist[2] to 2.",
                        "Round 2: no changes, break.",
                        "dist[1:] = [0, 2, 1]: the answer is <strong>2</strong>, through 1 → 3 → 2.",
                    ],
                ],
                "faq": [
                    ["Why <code>max(dist[1:])</code> and not <code>max(dist)</code>?",
                     "Nodes are labelled 1..n; index 0 is a dummy that stays infinite and would wrongly make every answer −1."],
                    ["Why can it stop early?",
                     "If a round changes nothing, no later round can either, because each round only uses the values the previous one left."],
                    ["When would I use Bellman–Ford over Dijkstra?",
                     "When edges can be negative, or when the number of edges on the path is limited, as in Cheapest Flights Within K Stops."],
                ],
            },
            "Floyd&ndash;Warshall": {
                "idea": [
                    "Compute the shortest distance between every pair of nodes, then read off row k.",
                    "Floyd–Warshall lets intermediate node m be used one at a time: the best i → j either avoids m or goes i → m → j.",
                ],
                "steps": [
                    "Make an (n + 1) × (n + 1) matrix <code>d</code> of infinity, with 0 on the diagonal.",
                    "For each edge, set <code>d[u][v] = min(d[u][v], w)</code> (keeping the cheapest of parallel edges).",
                    "For each <code>m</code>, then each <code>i</code> and <code>j</code>: if <code>d[i][m] + d[m][j] &lt; d[i][j]</code>, update it.",
                    "Take <code>best = max(d[k][1:])</code> and return −1 if it is infinite.",
                ],
                "why": [
                    "After processing m, <code>d[i][j]</code> is the shortest path using only intermediates 1..m; after all m, it is the true shortest distance.",
                    "Three nested loops over V: <strong>O(V³)</strong> time.",
                    "The full distance matrix: <strong>O(V²)</strong> space. It computes far more than one source needs.",
                ],
                "dry": [
                    [
                        "Direct entries: d[2][1]=1, d[2][3]=1, d[3][4]=1.",
                        "m=1 and m=2 improve nothing (no path passes through them usefully).",
                        "m=3: d[2][3] + d[3][4] = 2 &lt; ∞, so d[2][4] = 2. m=4 changes nothing.",
                        "Row 2 is [1, 0, 1, 2]: the answer is <strong>2</strong>.",
                    ],
                    [
                        "Direct: d[1][2]=4, d[1][3]=1, d[3][2]=1.",
                        "m=1 and m=2 improve nothing.",
                        "m=3: d[1][3] + d[3][2] = 2 &lt; 4, so d[1][2] = 2.",
                        "Row 1 is [0, 2, 1]: the answer is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>min</code> when loading edges?",
                     "The input may have two edges u → v with different times; only the faster one matters."],
                    ["Must <code>m</code> be the outer loop?",
                     "Yes. Each round relies on all paths through 1..m−1 being final; any other loop order can miss improvements."],
                    ["Is this a good choice here?",
                     "Only for tiny graphs. It answers all-pairs questions; for one source Dijkstra is much cheaper."],
                ],
            },
            "Dijkstra with a min-heap": {
                "idea": [
                    "With non-negative weights, the unsettled node with the smallest tentative distance already has its final distance.",
                    "A min-heap of <code>(distance, node)</code> pops nodes in increasing order of distance; each node is settled the first time it is popped.",
                ],
                "steps": [
                    "Build <code>adj</code> from the edges; start <code>heap = [(0, k)]</code> and an empty <code>dist</code> map.",
                    "Pop <code>(d, u)</code>. If <code>u</code> is already in <code>dist</code>, the entry is stale: skip it.",
                    "Otherwise settle <code>dist[u] = d</code>.",
                    "Push <code>(d + w, v)</code> for every unsettled neighbour <code>v</code>.",
                    "At the end, return <code>max(dist.values())</code> if all n nodes were settled, else −1.",
                ],
                "why": [
                    "Any other route to u passes through an entry with distance ≥ d and can only add non-negative weight, so the first pop of u is optimal.",
                    "Each edge pushes at most one entry, and each heap operation is O(log E) = O(log V): <strong>O(E log V)</strong> time.",
                    "The adjacency list, <code>dist</code> and the heap: <strong>O(V + E)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop (0, 2): dist[2]=0. Push (1, 1) and (1, 3).",
                        "Pop (1, 1): dist[1]=1, no edges. Pop (1, 3): dist[3]=1, push (2, 4).",
                        "Pop (2, 4): dist[4]=2.",
                        "All 4 nodes settled; the largest distance is <strong>2</strong>.",
                    ],
                    [
                        "Pop (0, 1): dist[1]=0. Push (4, 2) and (1, 3).",
                        "Pop (1, 3): dist[3]=1. Push (2, 2).",
                        "Pop (2, 2): dist[2]=2. Pop (4, 2): node 2 is settled, stale entry skipped.",
                        "All 3 nodes settled: <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the heap hold stale entries?",
                     "Pushing a better entry is easier than updating an old one in a heap. The old one surfaces later and is skipped by the <code>u in dist</code> check, as (4, 2) is in example 2."],
                    ["Why must weights be non-negative?",
                     "A negative edge could make a later path to an already-settled node shorter, breaking the \"first pop is final\" rule."],
                    ["How does it detect unreachable nodes?",
                     "They are never pushed, so <code>len(dist) &lt; n</code> and the answer is −1."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ path with minimum effort
    "path-minimum-effort": {
        "examples": [
            {"call": "minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]])", "expect": "2"},
            {"call": "minimum_effort_path([[1, 10], [2, 3]])", "expect": "1"},
        ],
        "approaches": {
            "Binary search on the effort, BFS to test it": {
                "idea": [
                    "Asking \"can I get across with effort at most <code>limit</code>?\" is easy: BFS using only steps whose height difference is ≤ limit.",
                    "The answer is monotone (a larger limit allows every path a smaller one did), so binary search for the smallest limit that works.",
                ],
                "steps": [
                    "<code>possible(limit)</code> runs a BFS from (0, 0), stepping only to in-grid, unseen cells with <code>abs(height difference) &lt;= limit</code>.",
                    "It returns <code>True</code> when the bottom-right cell is popped, <code>False</code> if the queue empties.",
                    "Search <code>lo = 0</code>, <code>hi = max height</code> (always enough).",
                    "If <code>possible(mid)</code>, set <code>hi = mid</code>; otherwise <code>lo = mid + 1</code>.",
                    "When <code>lo == hi</code>, return <code>lo</code>.",
                ],
                "why": [
                    "The loop keeps \"<code>hi</code> works, everything below <code>lo</code> fails\", so it ends on the smallest working limit.",
                    "Each BFS is O(m · n) and the search takes log H rounds: <strong>O(m · n · log H)</strong> time, H being the largest height.",
                    "One BFS's <code>seen</code> and queue: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0, hi=8. mid=4: possible → hi=4.",
                        "mid=2: the path 1 → 3 → 5 → 3 → 5 down the left and along the bottom has every step ≤ 2 → hi=2.",
                        "mid=1: from 1 only the three 2s are reachable; every way out of that area needs a step of 2 or more → lo=2.",
                        "lo == hi: the answer is <strong>2</strong>.",
                    ],
                    [
                        "lo=0, hi=10. mid=5: 1 → 2 → 3 works → hi=5. mid=2 → hi=2. mid=1 → hi=1.",
                        "mid=0: 1 → 2 needs effort 1, and the 10 is worse → lo=1.",
                        "lo == hi: the answer is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>hi = max height</code> safe?",
                     "Heights are non-negative, so no single step can differ by more than the largest height, and with that limit every neighbouring step is allowed."],
                    ["Why <code>hi = mid</code> and not <code>mid - 1</code> when it works?",
                     "mid itself may be the answer. Dropping it could skip past the smallest working limit."],
                    ["Can DFS replace BFS in <code>possible</code>?",
                     "Yes. Only reachability matters, not path length."],
                ],
            },
            "Union-find over edges sorted by difference": {
                "idea": [
                    "Think of each pair of neighbouring cells as an edge weighted by their height difference.",
                    "Add edges from cheapest to most expensive, Kruskal-style. The weight of the edge that first connects the two corners is the minimum possible maximum step.",
                ],
                "steps": [
                    "A 1 × 1 grid needs no steps: return 0.",
                    "List every down and right edge as <code>(diff, a, b)</code> with cells numbered <code>r * n + c</code>.",
                    "Create <code>parent</code> over all cells and a path-halving <code>find</code>.",
                    "For each edge in sorted order, union its endpoints.",
                    "As soon as <code>find(0) == find(m * n - 1)</code>, return the current weight <code>w</code>.",
                ],
                "why": [
                    "When the corners first connect, all edges used weigh ≤ w, so effort w is achievable. Before that, the cheaper edges alone did not connect them, so no path with a smaller maximum exists.",
                    "Sorting the ~2mn edges dominates: <strong>O(E log E)</strong> time.",
                    "The edge list and <code>parent</code>: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "Sorted edges begin: 0 (cells 1–2), 0 (2–5), 1 (0–1), then the weight-2 edges 0–3, 3–6, 6–7, 7–8.",
                        "After the 0s and the 1: {0, 1, 2, 5} is one set, but cell 8 is not in it.",
                        "Weight 2: 0–3, 3–6, 6–7 join the left column and bottom row; 7–8 finally reaches cell 8.",
                        "Corners 0 and 8 are connected at weight <strong>2</strong>.",
                    ],
                    [
                        "Cells: 0→1, 1→10, 2→2, 3→3. Sorted edges: (1, 0, 2), (1, 2, 3), (7, 1, 3), (9, 0, 1).",
                        "Union 0–2: corners not yet joined.",
                        "Union 2–3: now find(0) == find(3).",
                        "The answer is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why only down and right edges?",
                     "Each pair of neighbours needs one undirected edge. Adding up and left too would list every edge twice."],
                    ["Why the special case for a 1 × 1 grid?",
                     "There are no edges, so the loop never runs and the function would return <code>None</code>."],
                    ["How is this related to minimum spanning trees?",
                     "It is Kruskal's algorithm stopped early. A minimum spanning tree also minimises the largest edge on the path between any two nodes."],
                ],
            },
            "Dijkstra with max instead of sum": {
                "idea": [
                    "Run Dijkstra where a path's cost is its largest step, not the sum: extending a path to a new cell costs <code>max(e, step)</code>.",
                    "That cost never decreases along a path, which is all Dijkstra needs to settle cells in order of their best effort.",
                ],
                "steps": [
                    "Set <code>best</code> to infinity except <code>best[0][0] = 0</code>, and push <code>(0, 0, 0)</code>.",
                    "Pop <code>(e, r, c)</code>. If it is the bottom-right cell, return <code>e</code>.",
                    "If <code>e &gt; best[r][c]</code>, the entry is stale: skip it.",
                    "For each neighbour, compute <code>ne = max(e, abs(height difference))</code>.",
                    "If <code>ne &lt; best[a][b]</code>, record it and push <code>(ne, a, b)</code>.",
                ],
                "why": [
                    "Extending a path never lowers its effort, so the cell with the smallest effort on the heap cannot be improved later; the target's first pop is optimal.",
                    "Each cell has up to 4 edges and each push costs O(log(m · n)): <strong>O(m · n · log(m · n))</strong> time.",
                    "The <code>best</code> grid and the heap: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop (0,0,0): push (2,1,0) and (1,0,1). Pop (1,0,1): push (6,1,1) and (1,0,2).",
                        "Pop (1,0,2): push (1,1,2). Pop (1,1,2): the step down to 5 is 3, push (3,2,2).",
                        "Pop (2,1,0): push (2,2,0), and (5,1,1) improves on 6. Pop (2,2,0): push (2,2,1).",
                        "Pop (2,2,1): reaching the corner costs max(2, 2) = 2, better than 3, so push (2,2,2).",
                        "Pop (2,2,2): the target, so the answer is <strong>2</strong>.",
                    ],
                    [
                        "Pop (0,0,0): push (1,1,0) for the 2 and (9,0,1) for the 10.",
                        "Pop (1,1,0): the step to 3 is 1, so push (1,1,1).",
                        "Pop (1,1,1): the target, so the answer is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can I return as soon as the target is popped?",
                     "Pops come in non-decreasing order of effort, so no later entry can reach the target more cheaply."],
                    ["Why the stale check <code>e &gt; best[r][c]</code>?",
                     "A cell can be pushed several times as its effort improves; only the entry matching the current best should be expanded."],
                    ["Does Dijkstra work with max instead of sum in general?",
                     "Yes, for any path cost that never decreases when the path is extended; max of non-negative steps is one such cost."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ swim in rising water
    "swim-rising-water": {
        "examples": [
            {"call": "swim_in_water([[3, 2, 4], [0, 8, 1], [5, 7, 6]])", "expect": "6"},
            {"call": "swim_in_water([[0, 2], [1, 3]])", "expect": "3"},
        ],
        "approaches": {
            "Binary search on time, BFS to test it": {
                "idea": [
                    "At time t you can stand on any cell with elevation ≤ t, so \"can I swim across at time t?\" is a reachability test over those cells.",
                    "If it works at t it works at every later time, so binary search for the first t that works.",
                ],
                "steps": [
                    "<code>possible(t)</code> fails at once if <code>grid[0][0] &gt; t</code>.",
                    "Otherwise DFS from (0, 0) with a <code>stack</code>, moving only to unseen cells with <code>grid[a][b] &lt;= t</code>.",
                    "It returns <code>True</code> when (n−1, n−1) is popped.",
                    "Binary search on <code>lo = 0</code>, <code>hi = n * n - 1</code>: a working <code>mid</code> sets <code>hi = mid</code>, a failing one sets <code>lo = mid + 1</code>.",
                    "Return <code>lo</code>.",
                ],
                "why": [
                    "Higher water only adds cells, so success is monotone in t and the binary search finds the smallest successful t.",
                    "Each test is O(n²) and there are log(n²) tests: <strong>O(n² log n²)</strong> time.",
                    "One test's <code>seen</code> and stack: <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0, hi=8. mid=4: the swimmer reaches 3, 0, 2, 4 and 1 but every way to the corner needs 5, 6, 7 or 8 → lo=5.",
                        "mid=6: from 1 at (1,2) the corner 6 is now open → hi=6.",
                        "mid=5: the 5 below the 0 opens, but 7 and 6 still block → lo=6.",
                        "lo == hi: the answer is <strong>6</strong>.",
                    ],
                    [
                        "lo=0, hi=3. mid=1: cells 0 and 1 only; the corner 3 is closed → lo=2.",
                        "mid=2: 0, 1 and 2 are open, but the corner itself is 3 → lo=3.",
                        "lo == hi: the answer is <strong>3</strong>, the corner's own elevation.",
                    ],
                ],
                "faq": [
                    ["Why <code>hi = n * n - 1</code>?",
                     "Elevations are a permutation of 0..n²−1, so at that time every cell is open."],
                    ["Why check <code>grid[0][0] &gt; t</code> separately?",
                     "The search starts on (0, 0); if the start is still under the threshold you cannot even stand there."],
                    ["Why can the answer never be below the corner's elevation?",
                     "You must stand on the corner, so t ≥ grid[n−1][n−1]; example 2 is exactly that bound."],
                ],
            },
            "Dijkstra on the maximum elevation so far": {
                "idea": [
                    "Always step to the lowest cell bordering the area you have already reached, a min-heap keyed by elevation.",
                    "The time needed is the highest elevation ever popped on the way; once the corner is popped, that maximum is the answer.",
                ],
                "steps": [
                    "Push <code>(grid[0][0], 0, 0)</code>, mark (0, 0) in <code>seen</code>, and set <code>t = 0</code>.",
                    "Pop the lowest cell <code>(h, r, c)</code> and set <code>t = max(t, h)</code>.",
                    "If it is the bottom-right corner, return <code>t</code>.",
                    "Push every unseen in-grid neighbour with its elevation, marking it seen.",
                ],
                "why": [
                    "Cells are popped in the order the water would let you in: popping a cell of height h means nothing lower still borders your area, so the time must reach h before you can grow.",
                    "Each cell is pushed once, at O(log n²) per heap operation: <strong>O(n² log n)</strong> time.",
                    "<code>seen</code> and the heap: <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop 3 at (0,0): t=3. Push 0 and 2. Pop 0: t=3, push 5 and 8. Pop 2: push 4.",
                        "Pop 4: t=4, push 1. Pop 1: push 6.",
                        "The heap holds 5, 6 and 8. Pop 5: t=5, push 7.",
                        "Pop 6 at (2,2), the corner: t=6, so the answer is <strong>6</strong>.",
                    ],
                    [
                        "Pop 0: t=0, push 1 and 2.",
                        "Pop 1: t=1, push 3. Pop 2: t=2, the corner is already seen.",
                        "Pop 3, the corner: t=3, so the answer is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why mark cells seen when pushing rather than popping?",
                     "A cell's key is its fixed elevation, so a second entry could never be cheaper; marking early avoids duplicates."],
                    ["Why is <code>t</code> a running maximum, not the popped height?",
                     "Popped heights can go down again (4 then 1 in example 1); the water level never does."],
                    ["Is this really Dijkstra?",
                     "Yes, with path cost = maximum elevation on the path. It behaves like Prim's algorithm grown from (0, 0)."],
                ],
            },
            "Union-find, adding cells in order of elevation": {
                "idea": [
                    "Let the water rise one unit at a time. At time t exactly one new cell, the one with elevation t, becomes swimmable.",
                    "Union it with any neighbour that is already open; the first t at which the two corners share a set is the answer.",
                ],
                "steps": [
                    "Record <code>where[v]</code>, the position of elevation v.",
                    "Create <code>parent</code> over the n² cells, numbered <code>r * n + c</code>.",
                    "For <code>t</code> from 0 upward, take <code>(r, c) = where[t]</code>.",
                    "Union it with each in-grid neighbour whose elevation is ≤ t (already open).",
                    "If <code>find(0) == find(n * n - 1)</code>, return <code>t</code>.",
                ],
                "why": [
                    "After step t the sets are exactly the connected regions of cells with elevation ≤ t, so the first t joining the corners is the earliest time a swim is possible.",
                    "There are n² steps, each with 4 near-constant unions: <strong>O(n² · α)</strong> time.",
                    "<code>where</code> and <code>parent</code>: <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "t=0, 1, 2: cells (1,0), (1,2), (0,1) open, but no open neighbours yet.",
                        "t=3: (0,0) joins (1,0) and (0,1). t=4: (0,2) joins (1,2) and (0,1).",
                        "t=5: (2,0) joins (1,0). The corner (2,2) is still closed.",
                        "t=6: (2,2) opens and joins (1,2), which is in the start's set: the answer is <strong>6</strong>.",
                    ],
                    [
                        "t=0: (0,0) opens alone. t=1: (1,0) joins it.",
                        "t=2: (0,1) joins (0,0).",
                        "t=3: the corner (1,1) joins (0,1) and (1,0): the answer is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why test <code>grid[a][b] &lt;= t</code> for neighbours?",
                     "Only cells already under water (opened at an earlier or the current time) can be joined. Joining higher cells would let you swim through walls."],
                    ["Why can the corners' check run right after each new cell?",
                     "Connectivity only changes when a cell opens, so checking once per t catches the first moment they join."],
                    ["What makes this O(n²) rather than O(n² log n)?",
                     "Elevations are 0..n²−1, so <code>where</code> gives the opening order directly with no sorting or heap."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ cheapest flights within k stops
    "cheapest-flights-k-stops": {
        "examples": [
            {"call": "find_cheapest_price(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1)", "expect": "700"},
            {"call": "find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0)", "expect": "500"},
        ],
        "approaches": {
            "Bellman&ndash;Ford, k + 1 rounds": {
                "idea": [
                    "k stops means at most k + 1 flights. After round i of Bellman–Ford, <code>price</code> holds the cheapest cost using at most i flights.",
                    "Run exactly k + 1 rounds, and in each round read only last round's prices so a single round cannot chain two flights.",
                ],
                "steps": [
                    "Set <code>price</code> to infinity except <code>price[src] = 0</code>.",
                    "Repeat k + 1 times: copy <code>prev = price[:]</code>.",
                    "For each flight <code>(u, v, w)</code>, if <code>prev[u] + w &lt; price[v]</code>, set <code>price[v] = prev[u] + w</code>.",
                    "Return <code>price[dst]</code>, or −1 if it is still infinite.",
                ],
                "why": [
                    "Using <code>prev</code> means each round extends paths by exactly one flight, so after k + 1 rounds every route with at most k + 1 flights has been considered.",
                    "k + 1 rounds over E flights: <strong>O(k · E)</strong> time.",
                    "Two price arrays: <strong>O(V)</strong> space.",
                ],
                "dry": [
                    [
                        "price = [0, ∞, ∞, ∞]. Round 1 (prev = same): only 0→1 fires, price[1] = 100.",
                        "Round 2, prev = [0, 100, ∞, ∞]: 1→2 gives price[2] = 200 and 1→3 gives price[3] = 700.",
                        "2→3 would give 400, but it reads prev[2] = ∞, so it does not fire: that route needs 3 flights.",
                        "The answer is <strong>700</strong>.",
                    ],
                    [
                        "k = 0, so one round. prev = [0, ∞, ∞].",
                        "0→1 sets price[1] = 100; 1→2 reads prev[1] = ∞ and is skipped; 0→2 sets price[2] = 500.",
                        "The cheaper 200 route needs 2 flights and is never formed.",
                        "The answer is <strong>500</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong without the <code>prev</code> copy?",
                     "In example 1, 1→2 updates price[2] = 200 and then 2→3 reads it in the same round, giving 400 with 3 flights, which breaks the stop limit."],
                    ["Why compare against <code>price[v]</code> rather than <code>prev[v]</code>?",
                     "Several flights can land on v in one round; comparing with the running <code>price[v]</code> keeps the cheapest of them and the value from earlier rounds."],
                    ["Why k + 1 rounds?",
                     "A route with k stops has k + 1 flights, and each round adds one flight."],
                ],
            },
            "BFS by number of flights, with pruning": {
                "idea": [
                    "Explore level by level, where level i holds the cities reached with exactly i flights and their costs.",
                    "Only carry a city forward when this route beats every cheaper-or-equal one found so far; worse routes cannot lead anywhere better.",
                ],
                "steps": [
                    "Build <code>adj</code>; set <code>best</code> to infinity except <code>best[src] = 0</code>; <code>level = [(src, 0)]</code>.",
                    "Repeat k + 1 times: for each <code>(u, cost)</code> in <code>level</code> and flight <code>(v, w)</code>:",
                    "If <code>cost + w &lt; best[v]</code>, update <code>best[v]</code> and add <code>(v, cost + w)</code> to <code>nxt</code>.",
                    "Set <code>level = nxt</code>.",
                    "Return <code>best[dst]</code>, or −1 if infinite.",
                ],
                "why": [
                    "A route reaching v more expensively than an earlier one with fewer or equal flights can be replaced by that one, so pruning loses nothing within the flight limit.",
                    "Each level expands at most E flights over k + 1 levels: <strong>O(k · E)</strong> time.",
                    "The adjacency list, <code>best</code> and one level: <strong>O(V + E)</strong> space.",
                ],
                "dry": [
                    [
                        "level = [(0, 0)]. Round 1: 0→1 costs 100 → best[1] = 100, level = [(1, 100)].",
                        "Round 2: 1→2 costs 200 → best[2] = 200; 1→3 costs 700 → best[3] = 700.",
                        "level = [(2, 200), (3, 700)], but only k + 1 = 2 rounds run, so 2→3 is never tried.",
                        "The answer is <strong>700</strong>.",
                    ],
                    [
                        "level = [(0, 0)]. One round: 0→1 sets best[1] = 100, 0→2 sets best[2] = 500.",
                        "The loop ends; 1→2 would need a second flight.",
                        "The answer is <strong>500</strong>.",
                    ],
                ],
                "faq": [
                    ["Is the pruning <code>cost + w &lt; best[v]</code> safe?",
                     "Yes, because levels go in order of flight count: any route already in <code>best[v]</code> used no more flights, so a dearer later route is never better."],
                    ["Why not plain Dijkstra on cost?",
                     "The cheapest route may use too many flights. Dijkstra settles a city at its cheapest cost and can discard a pricier route with fewer flights that is the only valid one."],
                    ["How is this different from Bellman–Ford?",
                     "It only relaxes flights out of cities that improved last round, rather than every flight every round, but the bound is the same."],
                ],
            },
            "Dijkstra on (city, flights used)": {
                "idea": [
                    "Make the state a pair (city, flights used) and run Dijkstra on cost. The first time <code>dst</code> is popped, its cost is the cheapest within the limit.",
                    "A city popped again only helps if this route used fewer flights than every earlier (cheaper) visit; otherwise it is dominated.",
                ],
                "steps": [
                    "Build <code>adj</code>; <code>fewest[u]</code> is the fewest flights of any popped entry at <code>u</code>; push <code>(0, src, 0)</code>.",
                    "Pop <code>(cost, u, used)</code>. If <code>u == dst</code>, return <code>cost</code>.",
                    "Skip the entry if <code>used &gt;= fewest[u]</code> (a cheaper visit used no more flights) or <code>used &gt; k</code> (no flights left).",
                    "Otherwise set <code>fewest[u] = used</code> and push <code>(cost + w, v, used + 1)</code> for every flight.",
                    "If the heap empties, return −1.",
                ],
                "why": [
                    "Entries pop in cost order, so an earlier pop of u was cheaper; a later one is only useful when it has more flights left.",
                    "There are up to k · V useful states, each pushing its flights: <strong>O(k · E log(k · V))</strong> time.",
                    "The heap holds <strong>O(k · V)</strong> entries plus the graph.",
                ],
                "dry": [
                    [
                        "Pop (0, 0, 0): fewest[0] = 0, push (100, 1, 1).",
                        "Pop (100, 1, 1): 1 ≤ k, fewest[1] = 1. Push (200, 2, 2) and (700, 3, 2).",
                        "Pop (200, 2, 2): used 2 &gt; k = 1, skip.",
                        "Pop (700, 3, 2): it is dst, so the answer is <strong>700</strong>.",
                    ],
                    [
                        "Pop (0, 0, 0): push (100, 1, 1) and (500, 2, 1).",
                        "Pop (100, 1, 1): used 1 &gt; k = 0, skip; the cheap route dies here.",
                        "Pop (500, 2, 1): it is dst, so the answer is <strong>500</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is reaching dst with <code>used = k + 1</code> allowed?",
                     "<code>used</code> counts flights; k + 1 flights means k stops. The dst check runs before the <code>used &gt; k</code> check for exactly that reason."],
                    ["Why is <code>used &gt;= fewest[u]</code> a safe skip?",
                     "An earlier pop of u was at most as expensive and had at least as many flights left, so anything this entry can do, that one already did."],
                    ["What if I used a plain <code>visited</code> set on cities?",
                     "It can give wrong answers: a city first popped cheaply but with too many flights used would block a later, pricier visit that still has flights left."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reconstruct itinerary
    "reconstruct-itinerary": {
        "examples": [
            {"call": "find_itinerary([[\"JFK\", \"KUL\"], [\"JFK\", \"NRT\"], [\"NRT\", \"JFK\"]])", "expect": "[\"JFK\", \"NRT\", \"JFK\", \"KUL\"]"},
            {"call": "find_itinerary([[\"JFK\", \"SFO\"], [\"JFK\", \"ATL\"], [\"SFO\", \"ATL\"], [\"ATL\", \"JFK\"], [\"ATL\", \"SFO\"]])",
             "expect": "[\"JFK\", \"ATL\", \"JFK\", \"SFO\", \"ATL\", \"SFO\"]"},
        ],
        "approaches": {
            "DFS with backtracking, smallest destination first": {
                "idea": [
                    "Build the route greedily from JFK, always trying the alphabetically smallest unused ticket first, so the first complete route found is the lexically smallest.",
                    "A greedy choice can strand you with tickets left over; then undo it (backtrack) and try the next destination.",
                ],
                "steps": [
                    "Sort the tickets and build <code>adj</code>, so each airport's destinations are in alphabetical order.",
                    "Start <code>route = [\"JFK\"]</code>. <code>dfs(airport)</code> succeeds when <code>route</code> has <code>len(tickets) + 1</code> airports.",
                    "Try each destination <code>nxt</code> in order, skipping used ones (marked <code>None</code>).",
                    "Mark the ticket used, append <code>nxt</code> and recurse; on success return <code>True</code>.",
                    "On failure, pop <code>nxt</code> and restore the ticket, then try the next one.",
                ],
                "why": [
                    "Destinations are tried in alphabetical order at every step, so the search meets complete routes in lexical order and the first one is the answer.",
                    "Every complete route uses all tickets, which is what the length check tests.",
                    "Backtracking can retry many orders: exponential in the worst case, written <strong>O(E<sup>d</sup>)</strong> for maximum out-degree d. The route, adjacency lists and recursion use <strong>O(E)</strong> space.",
                ],
                "dry": [
                    [
                        "adj: JFK → [KUL, NRT], NRT → [JFK].",
                        "Try KUL: route [JFK, KUL]. KUL has no tickets and only 2 of 4 airports are placed: fail. Pop KUL and restore the ticket.",
                        "Try NRT: route [JFK, NRT], then NRT → JFK: [JFK, NRT, JFK].",
                        "From JFK, KUL is the only unused ticket: route has 4 airports, success.",
                        "The answer is <strong>[JFK, NRT, JFK, KUL]</strong>.",
                    ],
                    [
                        "adj: ATL → [JFK, SFO], JFK → [ATL, SFO], SFO → [ATL].",
                        "JFK → ATL (smallest), ATL → JFK, JFK → SFO (ATL is used).",
                        "SFO → ATL, ATL → SFO (JFK is used). 6 airports placed, success with no backtracking.",
                        "The answer is <strong>[JFK, ATL, JFK, SFO, ATL, SFO]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why mark a ticket <code>None</code> instead of removing it from the list?",
                     "Removing would shift the indices the loop is iterating over. Overwriting in place and restoring afterwards keeps the positions stable."],
                    ["Why is the first complete route the smallest?",
                     "Routes are compared airport by airport, and at every step the search tries the smallest available airport before any larger one."],
                    ["Why is this slow in the worst case?",
                     "Many dead ends can be explored deeply before backtracking. Hierholzer's algorithm never backtracks."],
                ],
            },
            "Hierholzer's algorithm": {
                "idea": [
                    "Using every ticket once is an <strong>Eulerian path</strong>. Hierholzer's algorithm walks greedily until stuck; the airport where you get stuck must be the end of the remaining route.",
                    "Recording airports as you get stuck builds the route backwards, and dead-end detours are automatically placed after the main loop.",
                ],
                "steps": [
                    "Sort tickets in reverse and append, so <code>adj[a].pop()</code> returns the smallest destination.",
                    "Start <code>stack = [\"JFK\"]</code> and an empty <code>route</code>.",
                    "While the top airport still has tickets, pop one and push its destination.",
                    "When the top has no tickets left, move it from <code>stack</code> to <code>route</code>.",
                    "When the stack empties, return <code>route[::-1]</code>.",
                ],
                "why": [
                    "An airport is moved to <code>route</code> only when all its outgoing tickets are used, so it can only come after everything still on the stack; reversing gives a valid order using every ticket once.",
                    "Taking the smallest ticket first means a dead end, when hit, is placed last, which keeps the result lexically smallest.",
                    "Each ticket is pushed and popped once, after an <strong>O(E log E)</strong> sort. The stack, route and lists take <strong>O(E)</strong> space.",
                ],
                "dry": [
                    [
                        "adj: JFK → [NRT, KUL] (pop gives KUL first), NRT → [JFK].",
                        "Pop KUL: stack [JFK, KUL]. KUL has no tickets: route = [KUL].",
                        "Top JFK still has NRT: stack [JFK, NRT, JFK]. JFK is now empty: route = [KUL, JFK].",
                        "NRT is empty: route = [KUL, JFK, NRT]. Then JFK: route = [KUL, JFK, NRT, JFK].",
                        "Reversed: <strong>[JFK, NRT, JFK, KUL]</strong>.",
                    ],
                    [
                        "adj: JFK → [SFO, ATL], ATL → [SFO, JFK], SFO → [ATL].",
                        "Walk: JFK → ATL → JFK → SFO → ATL → SFO; the stack holds all six airports.",
                        "SFO has no tickets left, and neither does anything below it, so all six move to route in reverse.",
                        "route = [SFO, ATL, SFO, JFK, ATL, JFK], reversed: <strong>[JFK, ATL, JFK, SFO, ATL, SFO]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is KUL placed in the route first in example 1?",
                     "The greedy walk went JFK → KUL and got stuck. A stuck airport has no tickets out, so it must be the last stop overall, which is the first one recorded."],
                    ["Why sort in reverse?",
                     "Python's <code>list.pop()</code> takes from the end, so storing destinations in descending order makes it return the smallest."],
                    ["Does this need backtracking for dead ends?",
                     "No. A dead end is simply recorded early and ends up at the end of the reversed route, while the rest of the tickets are spliced in before it."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ min cost to connect all points
    "min-cost-connect-points": {
        "examples": [
            {"call": "min_cost_connect_points([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]])", "expect": "20"},
            {"call": "min_cost_connect_points([[3, 12], [-2, 5], [-4, 1]])", "expect": "18"},
        ],
        "approaches": {
            "Kruskal: sort all edges, union-find": {
                "idea": [
                    "Every pair of points is an edge weighted by Manhattan distance; the answer is the weight of a <strong>minimum spanning tree</strong>.",
                    "Kruskal takes edges from cheapest upward and keeps each one that joins two different components; n − 1 kept edges form the tree.",
                ],
                "steps": [
                    "Build <code>edges</code> as <code>(distance, i, j)</code> for every <code>i &lt; j</code> and sort them.",
                    "Create <code>parent</code> with a path-halving <code>find</code>.",
                    "For each edge, if <code>find(i) != find(j)</code>, union them, add <code>w</code> to <code>total</code> and count it in <code>used</code>.",
                    "Stop once <code>used == n - 1</code>.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "The cheapest edge crossing any cut between components is always safe to add (the cut property), and Kruskal only adds such edges.",
                    "There are n(n − 1)/2 edges and sorting dominates: <strong>O(n² log n)</strong> time.",
                    "The edge list holds <strong>O(n²)</strong> entries.",
                ],
                "dry": [
                    [
                        "Sorted edges begin: 3 (1–3), 4 (0–1), 4 (3–4), 7 (0–3), 7 (0–4), 7 (1–4), 9 (1–2), …",
                        "Take 1–3 (3), 0–1 (4), 3–4 (4): {0, 1, 3, 4} are joined, total = 11.",
                        "All three weight-7 edges connect points already joined, so they are skipped.",
                        "Take 1–2 (9): used = 4 = n − 1, stop. Total <strong>20</strong>.",
                    ],
                    [
                        "Distances: 1–2 = 6, 0–1 = 12, 0–2 = 18.",
                        "Take 1–2 (6), then 0–1 (12): used = 2 = n − 1, stop.",
                        "Total <strong>18</strong>.",
                    ],
                ],
                "faq": [
                    ["Why skip an edge whose endpoints share a root?",
                     "It would close a cycle. The two points are already connected more cheaply, so the edge adds cost without connecting anything."],
                    ["Why stop at n − 1 edges?",
                     "A spanning tree on n points has exactly n − 1 edges, so the rest of the sorted list can only be skipped."],
                    ["What does a single point return?",
                     "There are no edges, the loop does nothing and <code>total = 0</code>, which is right."],
                ],
            },
            "Prim with a min-heap": {
                "idea": [
                    "Grow one tree from point 0. At each step, attach the outside point that is cheapest to connect to the tree.",
                    "A heap of <code>(cost, point)</code> candidates gives that cheapest point; stale entries for points already in the tree are skipped.",
                ],
                "steps": [
                    "Start with <code>heap = [(0, 0)]</code>, an empty <code>seen</code> and <code>total = 0</code>.",
                    "Pop <code>(w, i)</code>; if <code>i</code> is in <code>seen</code>, skip it.",
                    "Otherwise add <code>i</code> to the tree and <code>w</code> to <code>total</code>.",
                    "Push the distance from <code>i</code> to every point not yet in the tree.",
                    "Stop once all n points are in <code>seen</code>; return <code>total</code>.",
                ],
                "why": [
                    "Each pop is the cheapest edge leaving the current tree, which the cut property says belongs to some minimum spanning tree.",
                    "Up to n pushes per added point: O(n²) heap entries at O(log n) each, <strong>O(n² log n)</strong> time.",
                    "The heap can hold <strong>O(n²)</strong> entries.",
                ],
                "dry": [
                    [
                        "Pop (0, 0): total 0. Push 4→1, 13→2, 7→3, 7→4.",
                        "Pop (4, 1): total 4. Push 9→2, 3→3, 7→4. Pop (3, 3): total 7. Push 10→2, 4→4.",
                        "Pop (4, 4): total 11. Push 14→2.",
                        "Pop (7, 3), (7, 4), (7, 4): all stale. Pop (9, 2): total <strong>20</strong>.",
                    ],
                    [
                        "Pop (0, 0): push 12→1, 18→2.",
                        "Pop (12, 1): total 12. Push 6→2.",
                        "Pop (6, 2): total <strong>18</strong>; the (18, 2) entry is never needed.",
                    ],
                ],
                "faq": [
                    ["Why can a point be in the heap several times?",
                     "Each new tree point pushes a fresh distance to it. Only the first pop (the cheapest) counts; the others are skipped by the <code>seen</code> check."],
                    ["Why start with cost 0 for point 0?",
                     "The first point joins the tree for free; that entry just seeds the loop."],
                    ["Kruskal or Prim here?",
                     "Both are O(n² log n) on a complete graph. The array version of Prim below is better still at O(n²)."],
                ],
            },
            "Prim with a distance array (dense graphs)": {
                "idea": [
                    "On a complete graph a heap is wasted effort. Keep <code>dist[j]</code>, the cheapest known connection from point j to the tree, and pick the minimum by a linear scan.",
                    "After adding a point, one pass updates every outside point's <code>dist</code>.",
                ],
                "steps": [
                    "Set <code>dist</code> to infinity except <code>dist[0] = 0</code>, and <code>in_tree</code> to all False.",
                    "Repeat n times: pick the outside point <code>i</code> with the smallest <code>dist</code>.",
                    "Mark it <code>in_tree</code> and add <code>dist[i]</code> to <code>total</code>.",
                    "For every outside point <code>j</code>, lower <code>dist[j]</code> to the distance from <code>i</code> if that is smaller.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "<code>dist[j]</code> is always the cheapest edge from j into the tree, so each chosen point is attached by the cheapest crossing edge, as Prim requires.",
                    "n rounds, each with an O(n) scan and an O(n) update: <strong>O(n²)</strong> time with no edge list.",
                    "Two arrays of length n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Add 0: dist = [0, 4, 13, 7, 7].",
                        "Add 1 (4): total 4; dist[2] → 9, dist[3] → 3, dist[4] stays 7.",
                        "Add 3 (3): total 7; dist[4] → 4. Add 4 (4): total 11; dist[2] stays 9.",
                        "Add 2 (9): total <strong>20</strong>.",
                    ],
                    [
                        "Add 0: dist = [0, 12, 18].",
                        "Add 1 (12): total 12; dist[2] → 6.",
                        "Add 2 (6): total <strong>18</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is this faster than the heap version here?",
                     "With n² edges the heap does n² pushes at log n each. The array does n scans of n, with no log factor."],
                    ["Is the linear scan for the minimum not slow?",
                     "It is O(n) per round, but the update pass is O(n) anyway, so the scan costs nothing extra in the bound."],
                    ["When is the heap version better?",
                     "On sparse graphs with far fewer than n² edges, where updating every point each round would waste time."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ alien dictionary
    "alien-dictionary": {
        "examples": [
            {"call": "alien_order([\"wrt\", \"wrf\", \"er\", \"ett\", \"rftt\"])", "expect": "\"wertf\""},
            {"call": "alien_order([\"z\", \"x\", \"z\"])", "expect": "\"\""},
        ],
        "approaches": {
            "Adjacent-pair edges, DFS post-order": {
                "idea": [
                    "Neighbouring words in the sorted list reveal one fact each: at their first differing position, the upper letter comes before the lower one.",
                    "These facts are edges between letters; any topological order of that graph is a valid alphabet, and a cycle means none exists.",
                    "A word followed by its own proper prefix (\"abc\" before \"ab\") is impossible, so return \"\" at once.",
                ],
                "steps": [
                    "Create <code>adj</code> with an empty set for every letter that appears.",
                    "For each adjacent pair <code>(a, b)</code>, find the first differing letters <code>x, y</code> and add <code>x → y</code>, then break.",
                    "If there is no difference (the <code>for</code>'s <code>else</code>) and <code>a</code> is longer, return \"\".",
                    "Run a grey/black DFS from every letter, appending each to <code>out</code> when it finishes; a grey neighbour means a cycle: return \"\".",
                    "Return <code>out</code> reversed and joined.",
                ],
                "why": [
                    "Only the first difference carries information; letters after it are unordered by that pair, so stopping there avoids false edges.",
                    "Reversed post-order puts every letter before the letters it must precede, as in Course Schedule II.",
                    "Building edges reads every character once: <strong>O(C)</strong> for C total characters. The graph has at most 26 nodes: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Pairs: wrt/wrf gives t → f; wrf/er gives w → e; er/ett gives r → t; ett/rftt gives e → r.",
                        "adj keys in first-seen order: w, r, t, f, e.",
                        "dfs(w) → e → r → t → f. f finishes first: out = [f, t, r, e, w].",
                        "The other letters are already black. Reversed: <strong>\"wertf\"</strong>.",
                    ],
                    [
                        "Pairs: z/x gives z → x; x/z gives x → z.",
                        "dfs(z) turns z grey, visits x, which sees z still grey: a cycle.",
                        "The result is <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why break after the first differing letter?",
                     "Dictionary order is decided by the first difference; later letters say nothing. \"wrt\" before \"wrf\" does not mean anything about letters after t and f."],
                    ["Why does a longer word before its prefix make the input invalid?",
                     "In any alphabet a prefix sorts before its extensions, so \"abc\" before \"ab\" cannot happen in a sorted list."],
                    ["Why put every letter in <code>adj</code>, even with no edges?",
                     "Letters with no constraints still belong in the alphabet. Without their own keys they would never be visited and would be missing from the answer."],
                ],
            },
            "Adjacent-pair edges, Kahn's algorithm": {
                "idea": [
                    "Same letter graph from adjacent word pairs, but ordered with Kahn's algorithm: repeatedly output a letter with no remaining predecessors.",
                    "If some letters never become free, they sit on a cycle and the answer is \"\".",
                ],
                "steps": [
                    "Create <code>adj</code> and <code>indeg</code> for every letter.",
                    "For each adjacent pair, add the first-difference edge <code>x → y</code> only if new, raising <code>indeg[y]</code>; return \"\" for the prefix case.",
                    "Queue every letter with in-degree 0.",
                    "Pop <code>u</code>, append it to <code>out</code>, and decrement each successor, queuing those that reach 0.",
                    "Return the joined <code>out</code> if it has every letter, otherwise \"\".",
                ],
                "why": [
                    "A letter is output only after all letters that must precede it, so <code>out</code> respects every constraint.",
                    "Letters on a cycle never reach in-degree 0, so a short <code>out</code> correctly signals an impossible order.",
                    "<strong>O(C)</strong> time to read the words, and the graph is bounded by 26 letters: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Edges t → f, w → e, r → t, e → r. In-degrees: w 0, others 1.",
                        "Queue [w]. Pop w → e is free. Pop e → r is free.",
                        "Pop r → t is free. Pop t → f is free. Pop f.",
                        "All 5 letters output: <strong>\"wertf\"</strong>.",
                    ],
                    [
                        "Edges z → x and x → z; both in-degrees are 1.",
                        "No letter starts free, so the queue is empty.",
                        "out has 0 of 2 letters: <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>if y not in adj[x]</code> before raising the in-degree?",
                     "The same edge can come from several word pairs. The set stores it once, so the in-degree must count it once, or y would never reach 0."],
                    ["Is the answer unique?",
                     "Not in general; letters without constraints between them can go in any order. Example 1 has a single chain, so only one answer exists."],
                    ["DFS or Kahn here?",
                     "Both are linear. Kahn avoids recursion and makes the cycle test a simple length comparison."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ critical and pseudo-critical edges
    "critical-pseudo-critical-edges": {
        "examples": [
            {"call": "find_critical_and_pseudo_critical_edges(4, [[0, 1, 1], [1, 2, 2], [0, 2, 2], [2, 3, 3]])", "expect": "[[0, 3], [1, 2]]"},
            {"call": "find_critical_and_pseudo_critical_edges(4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 1]])", "expect": "[[], [0, 1, 2, 3]]"},
        ],
        "approaches": {
            "Kruskal once per edge, excluded and forced": {
                "idea": [
                    "An edge is <strong>critical</strong> if removing it makes the minimum spanning tree heavier (or impossible).",
                    "Otherwise it is <strong>pseudo-critical</strong> if some MST can still contain it: forcing it in first and finishing with Kruskal gives the optimal weight.",
                    "So compute the true MST weight once, then run Kruskal twice per edge: once skipping it, once forcing it.",
                ],
                "steps": [
                    "Sort edge indices by weight into <code>order</code>.",
                    "<code>mst(skip, force)</code> runs Kruskal with a fresh <code>parent</code>; a forced edge is unioned first and its weight counted.",
                    "It returns the total weight, or infinity if fewer than n − 1 edges were used (the graph fell apart).",
                    "Compute <code>best = mst()</code>.",
                    "For each edge i: if <code>mst(skip=i) &gt; best</code>, it is critical; else if <code>mst(force=i) == best</code>, it is pseudo-critical.",
                ],
                "why": [
                    "Skipping i still finds the best tree without i, so a heavier result proves every MST needs i.",
                    "Forcing i finds the best tree that contains i; if that equals <code>best</code>, some MST uses i.",
                    "About 2E Kruskal runs of O(E · α(V)) each after one sort: <strong>O(E² · α(V))</strong> time, with <strong>O(V + E)</strong> space.",
                ],
                "dry": [
                    [
                        "order = [0, 1, 2, 3]. best: take e0 (1), e1 (2), skip e2, take e3 (3) → 6.",
                        "Skip e0: e1 + e2 + e3 = 7 &gt; 6, so e0 is critical.",
                        "Skip e1: 6, not heavier. Force e1: 2 + 1 + 3 = 6, pseudo-critical. e2 behaves the same way.",
                        "Skip e3: node 3 is cut off, only 2 edges used → ∞ &gt; 6, critical.",
                        "The result is <strong>[[0, 3], [1, 2]]</strong>.",
                    ],
                    [
                        "A 4-cycle of weight-1 edges: best = 3.",
                        "Skipping any edge leaves a path of three edges, still 3, so none is critical.",
                        "Forcing any edge and adding two more also gives 3, so all are pseudo-critical.",
                        "The result is <strong>[[], [0, 1, 2, 3]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why test pseudo-critical only when the edge is not critical?",
                     "A critical edge is in every MST and would also pass the forcing test, but the two lists must not overlap."],
                    ["Why return infinity when fewer than n − 1 edges are used?",
                     "Without a bridge the graph is disconnected and no spanning tree exists; infinity makes such a bridge count as critical, as e3 is in example 1."],
                    ["Can an edge be neither?",
                     "Yes. An edge heavier than every alternative, such as a weight-6 edge closing a cycle of lighter ones, is in no MST: forcing it gives a weight above <code>best</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ build a matrix with conditions
    "build-matrix-conditions": {
        "examples": [
            {"call": "build_matrix(3, [[1, 2], [2, 3]], [[3, 2], [2, 1]])", "expect": "[[0, 0, 1], [0, 2, 0], [3, 0, 0]]"},
            {"call": "build_matrix(2, [[1, 2], [2, 1]], [[1, 2]])", "expect": "[]"},
        ],
        "approaches": {
            "Two topological sorts with DFS": {
                "idea": [
                    "Row conditions and column conditions are independent: rows only constrain which row each number gets, columns only which column.",
                    "Each set of conditions is a graph on 1..k; a topological order gives every number a row (or column) index. Placing number v at (row of v, column of v) uses a distinct row and column, so nothing collides.",
                ],
                "steps": [
                    "<code>topo(conds)</code> builds <code>adj</code> with edges <code>a → b</code> and runs a grey/black DFS over 1..k.",
                    "Each finished node is appended to <code>out</code>; a grey neighbour means a cycle, and <code>topo</code> returns <code>None</code>.",
                    "Otherwise it returns <code>out[::-1]</code>.",
                    "Compute <code>rows</code> and <code>cols</code>; if either is <code>None</code>, return <code>[]</code>.",
                    "Map each value to its position (<code>r_of</code>, <code>c_of</code>) and write <code>M[r_of[v]][c_of[v]] = v</code>.",
                ],
                "why": [
                    "In a topological order every a precedes b, so <code>r_of[a] &lt; r_of[b]</code> for each row condition, which puts a strictly above b; columns work the same way.",
                    "Each number has a unique row and a unique column, so the k values fill k distinct cells.",
                    "Two DFS runs over k nodes and n conditions: <strong>O(k + n)</strong> time and <strong>O(k + n)</strong> space for the graphs (the k × k output itself adds k²).",
                ],
                "dry": [
                    [
                        "Rows: 1 → 2 → 3. dfs(1) → dfs(2) → dfs(3), out = [3, 2, 1], so rows = [1, 2, 3].",
                        "Columns: 3 → 2 → 1. dfs(1) finishes first, then 2, then 3: out = [1, 2, 3], so cols = [3, 2, 1].",
                        "1 goes to (0, 2), 2 to (1, 1), 3 to (2, 0).",
                        "The result is <strong>[[0, 0, 1], [0, 2, 0], [3, 0, 0]]</strong>.",
                    ],
                    [
                        "Rows: 1 → 2 and 2 → 1. dfs(1) visits 2, which sees 1 still grey: a cycle, so rows is None.",
                        "Columns sort fine to [1, 2], but rows already failed.",
                        "The result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can rows and columns be solved separately?",
                     "No condition mixes them. Any row order and any column order combine into a valid matrix because each number gets its own row and column."],
                    ["What about numbers that appear in no condition?",
                     "The outer loop runs over all of 1..k, so they are still placed somewhere in the order."],
                    ["Do duplicate conditions cause problems?",
                     "No. Repeated edges are just revisited black nodes in the DFS."],
                ],
            },
            "Two topological sorts with Kahn's algorithm": {
                "idea": [
                    "Same reduction: one topological order for rows, one for columns, then place each number at (its row index, its column index).",
                    "Kahn's algorithm produces each order iteratively and detects a cycle when it cannot output all k numbers.",
                ],
                "steps": [
                    "<code>topo(conds)</code> builds <code>adj</code> and <code>indeg</code> for 1..k.",
                    "Queue the numbers with in-degree 0, then pop, append to <code>out</code>, and free successors whose in-degree reaches 0.",
                    "Return <code>out</code> if it has k numbers, else <code>None</code>.",
                    "If either order is <code>None</code>, return <code>[]</code>.",
                    "Otherwise fill <code>M</code> using the position maps <code>r_of</code> and <code>c_of</code>.",
                ],
                "why": [
                    "A number is output only after all numbers that must precede it, so the order satisfies every condition.",
                    "Numbers on a cycle are never freed, so a short <code>out</code> means no valid matrix exists.",
                    "Linear in nodes plus conditions: <strong>O(k + n)</strong> time and <strong>O(k + n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "Rows: in-degrees 2 → 1, 3 → 1; queue [1]. Output 1, then 2, then 3: rows = [1, 2, 3].",
                        "Columns: 3 → 2 → 1; only 3 starts free. cols = [3, 2, 1].",
                        "Placing each value at (row, column) gives (0, 2), (1, 1), (2, 0).",
                        "The result is <strong>[[0, 0, 1], [0, 2, 0], [3, 0, 0]]</strong>.",
                    ],
                    [
                        "Rows: 1 → 2 and 2 → 1, both in-degree 1, so the queue starts empty.",
                        "out has 0 of 2 numbers, so rows is None.",
                        "The result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>indeg</code> have size k + 1?",
                     "Numbers run from 1 to k; index 0 is unused so the values can index the array directly."],
                    ["Do duplicate conditions break the in-degree counts?",
                     "No. Each duplicate adds both an edge and an in-degree, and each edge is decremented once, so they cancel."],
                    ["Why is the answer not unique?",
                     "Any valid pair of orders works. The tests check the conditions rather than one exact matrix; this example has only one solution."],
                ],
            },
        },
    },
}
