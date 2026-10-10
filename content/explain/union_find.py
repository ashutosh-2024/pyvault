"""Write-ups for the Union-Find topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ number of connected components
    "count-connected-components": {
        "examples": [
            {"call": "count_components(6, [[0, 1], [1, 2], [3, 4], [2, 0]])", "expect": "3"},
            {"call": "count_components(4, [[0, 1], [2, 3], [1, 3]])", "expect": "1"},
        ],
        "approaches": {
            "DFS from every unvisited node": {
                "idea": [
                    "A component is everything reachable from one node, so a single traversal from any node marks exactly one whole component.",
                    "Starting a fresh traversal only from nodes no earlier traversal has reached means each start is a <strong>new</strong> component: count the starts.",
                ],
                "steps": [
                    "Build an adjacency list <code>adj</code>, adding each undirected edge in both directions.",
                    "Keep <code>seen</code> (one flag per node) and <code>count = 0</code>.",
                    "Loop <code>start</code> over 0..n−1. If <code>seen[start]</code> is already set, skip it: an earlier traversal covered it.",
                    "Otherwise add 1 to <code>count</code>, mark <code>start</code> seen and push it on <code>stack</code>.",
                    "Pop nodes off the stack; push every neighbour <code>nb</code> not yet seen, marking it as it is pushed. When the stack empties the component is fully marked.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Every node of a component is reachable from its first-seen node, so one traversal marks the whole component and no later start lands inside it.",
                    "Isolated nodes have no edges but are still visited by the outer loop, so each counts as its own component.",
                    "Each node is pushed once and each adjacency list is scanned once: <strong>O(V + E)</strong> time. The adjacency list, flags and stack take <strong>O(V + E)</strong> space.",
                ],
                "dry": [
                    [
                        "adj: 0→[1, 2], 1→[0, 2], 2→[1, 0], 3→[4], 4→[3], 5→[].",
                        "start=0: count=1. Pop 0, push 1 and 2. Pop 2 (both neighbours seen), pop 1. Nodes 0, 1, 2 are marked.",
                        "start=1, 2: already seen, skipped.",
                        "start=3: count=2. Pop 3, push 4. Pop 4. start=4 is skipped.",
                        "start=5: count=3, no neighbours. The answer is <strong>3</strong>.",
                    ],
                    [
                        "adj: 0→[1], 1→[0, 3], 2→[3], 3→[2, 1].",
                        "start=0: count=1. Pop 0, push 1. Pop 1, push 3 (0 is seen).",
                        "Pop 3, push 2. Pop 2: its neighbour 3 is seen. The stack is empty.",
                        "start=1, 2, 3 are all seen, so the answer is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why mark a node when it is pushed instead of when it is popped?",
                     "Marking on push stops the same node from entering the stack twice through two different neighbours. Marking on pop still gives the right count but can push duplicates."],
                    ["Does the duplicate edge <code>[2, 0]</code> in example 1 cause trouble?",
                     "No. It only adds extra neighbour entries; they are already seen when scanned, so nothing is pushed twice and the count is unaffected."],
                    ["Recursive DFS or BFS instead of the explicit stack?",
                     "Any traversal works because only reachability matters. The explicit stack avoids Python's recursion limit on long chains."],
                ],
            },
            "Union-find, one decrement per successful union": {
                "idea": [
                    "Start with every node as its own component, so <code>count = n</code>.",
                    "An edge either joins two different components, which reduces the count by exactly one, or lies inside one component and changes nothing.",
                    "A disjoint-set structure answers \"same component?\" through <code>find</code> and merges two sets in near-constant time.",
                ],
                "steps": [
                    "Create <code>parent = list(range(n))</code> and <code>size = [1] * n</code>: every node is a root of a one-node tree.",
                    "<code>find(x)</code> walks up to the root, and with path halving points each visited node at its grandparent on the way.",
                    "For each edge <code>(a, b)</code>, compute the roots <code>ra</code> and <code>rb</code>.",
                    "If <code>ra == rb</code>, the edge is redundant: skip it.",
                    "Otherwise swap so <code>ra</code> is the larger tree, hang <code>rb</code> under it, add the sizes and decrement <code>count</code>.",
                    "Return <code>count</code> after all edges.",
                ],
                "why": [
                    "Two nodes share a root exactly when the edges processed so far connect them, so every decrement merges two genuinely separate components.",
                    "The count starts at n and drops once per merge, so it always equals the number of sets.",
                    "Union by size plus path halving makes each operation amortised α(V), almost constant: <strong>O(V + E · α(V))</strong> time.",
                    "Only <code>parent</code> and <code>size</code> are stored, so space is <strong>O(V)</strong>; no adjacency list is ever built.",
                ],
                "dry": [
                    [
                        "count=6. Edge (0,1): roots 0 and 1, equal sizes, so 1 goes under 0. size[0]=2, count=5.",
                        "Edge (1,2): find(1)=0, find(2)=2. size[0]=2 &gt; 1, so 2 goes under 0. size[0]=3, count=4.",
                        "Edge (3,4): 4 goes under 3, count=3.",
                        "Edge (2,0): find(2)=0 and find(0)=0, the same root, so the edge is skipped.",
                        "Node 5 never appears in an edge and stays its own set. The answer is <strong>3</strong>.",
                    ],
                    [
                        "count=4. Edge (0,1): 1 goes under 0, size[0]=2, count=3.",
                        "Edge (2,3): 3 goes under 2, size[2]=2, count=2.",
                        "Edge (1,3): find(1)=0, find(3)=2. Sizes tie at 2, so no swap: 2 goes under 0, size[0]=4.",
                        "count=1. The answer is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why decrement only when the roots differ?",
                     "An edge inside one component closes a cycle and connects nothing new. Decrementing for it would undercount; in example 1 the edge (2, 0) would give 2 instead of 3."],
                    ["What does union by size buy?",
                     "Hanging the smaller tree under the larger keeps trees shallow, so <code>find</code> stays fast even for adversarial edge orders such as a long chain."],
                    ["When is union-find better than DFS here?",
                     "When edges arrive one at a time (an online stream) or the count is needed after each edge. DFS needs the whole graph built first."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ graph valid tree
    "graph-valid-tree": {
        "examples": [
            {"call": "valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3]])", "expect": "False"},
            {"call": "valid_tree(5, [[0, 1], [0, 2], [0, 3], [1, 4]])", "expect": "True"},
        ],
        "approaches": {
            "Edge count, then DFS for connectivity": {
                "idea": [
                    "A graph on n nodes is a tree exactly when it is <strong>connected</strong> and has <strong>n − 1 edges</strong>; either condition plus the edge count rules out cycles.",
                    "The edge count is a free O(1) check, so only connectivity needs a traversal.",
                ],
                "steps": [
                    "If <code>len(edges) != n - 1</code>, return <code>False</code> immediately.",
                    "Build an undirected adjacency list <code>adj</code>.",
                    "Run an iterative DFS from node 0 with <code>seen = {0}</code> and <code>stack = [0]</code>.",
                    "Pop a node and push every neighbour not in <code>seen</code>, adding it to <code>seen</code> at once.",
                    "Return <code>len(seen) == n</code>: true only if every node was reached.",
                ],
                "why": [
                    "A connected graph with n − 1 edges has no cycle, because a cycle could lose an edge and stay connected, leaving a connected graph with n − 2 edges, which is impossible.",
                    "So once the count passes, reaching all n nodes from 0 proves the graph is a tree, and missing any node proves it is not.",
                    "The DFS touches each node and edge once: <strong>O(V + E)</strong> time, with <strong>O(V + E)</strong> space for the adjacency list and <code>seen</code>.",
                ],
                "dry": [
                    [
                        "There are 4 edges and n − 1 = 4, so the count check passes.",
                        "adj: 0→[1], 1→[0, 2, 3], 2→[1, 3], 3→[2, 1], 4→[].",
                        "Pop 0, add 1. Pop 1, add 2 and 3. Pop 3, pop 2: nothing new.",
                        "seen = {0, 1, 2, 3}, size 4 ≠ 5: node 4 is cut off (the spent edge went into the cycle 1-2-3). Result <strong>False</strong>.",
                    ],
                    [
                        "4 edges, n − 1 = 4: the count check passes.",
                        "adj: 0→[1, 2, 3], 1→[0, 4], 2→[0], 3→[0], 4→[1].",
                        "Pop 0, add 1, 2, 3. Pop 3, pop 2. Pop 1, add 4. Pop 4.",
                        "seen has all 5 nodes, so the result is <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can I skip cycle detection entirely?",
                     "With exactly n − 1 edges, connected and acyclic are equivalent. Checking connectivity alone is enough."],
                    ["What about n = 1 with no edges?",
                     "The count check passes (0 == 0) and the DFS sees node 0, so <code>len(seen) == 1</code> and the answer is <code>True</code>: a single node is a tree."],
                    ["Why start from node 0 specifically?",
                     "Any node works for a connectivity test; 0 always exists because n ≥ 1."],
                ],
            },
            "Edge count, then union-find for cycles": {
                "idea": [
                    "After the n − 1 edge check, a tree is the same thing as an acyclic graph, so only cycles need detecting.",
                    "Union-find spots a cycle the moment an edge joins two nodes that already share a root.",
                ],
                "steps": [
                    "If <code>len(edges) != n - 1</code>, return <code>False</code>.",
                    "Create <code>parent = list(range(n))</code> and a <code>find</code> with path halving.",
                    "For each edge <code>(a, b)</code>, compute <code>ra = find(a)</code> and <code>rb = find(b)</code>.",
                    "If <code>ra == rb</code>, the endpoints are already connected and this edge closes a cycle: return <code>False</code>.",
                    "Otherwise link <code>parent[ra] = rb</code>. If every edge merges two sets, return <code>True</code>.",
                ],
                "why": [
                    "n − 1 edges that each merge two different sets reduce n singletons to exactly one set, so the graph is connected and acyclic.",
                    "If any edge fails to merge, it lies on a cycle, so the graph is not a tree.",
                    "Each <code>find</code> is near constant amortised, giving <strong>O(V + E · α(V))</strong> time and <strong>O(V)</strong> space for <code>parent</code>.",
                ],
                "dry": [
                    [
                        "4 edges, the count check passes. parent = [0, 1, 2, 3, 4].",
                        "(0,1): roots 0, 1 → parent[0]=1. (1,2): roots 1, 2 → parent[1]=2.",
                        "(2,3): roots 2, 3 → parent[2]=3.",
                        "(1,3): find(1) climbs 1 → 2 → 3 (halving sets parent[1]=3); find(3)=3. Same root, so this edge closes the cycle 1-2-3: <strong>False</strong>.",
                    ],
                    [
                        "parent = [0, 1, 2, 3, 4]. (0,1): parent[0]=1.",
                        "(0,2): find(0)=1, find(2)=2 → parent[1]=2.",
                        "(0,3): find(0) climbs to 2 → parent[2]=3. (1,4): find(1)=3 → parent[3]=4.",
                        "All four edges merged two different sets, so the result is <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Example 1 is unconnected. Why does it fail on a cycle instead?",
                     "With exactly n − 1 edges, a disconnected graph must contain a cycle somewhere, so the cycle check catches it. Here the edge (1, 3) closes 1-2-3 before node 4 matters."],
                    ["Is the n − 1 check still needed with union-find?",
                     "Yes. Without it, a forest such as <code>valid_tree(4, [[0, 1], [2, 3]])</code> has no cycle and would be accepted, though it is not connected."],
                    ["There is no union by size here. Is that a problem?",
                     "Path halving alone still keeps operations cheap in practice (amortised O(log n)); adding size or rank would give the textbook α bound."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ redundant connection
    "redundant-connection": {
        "examples": [
            {"call": "find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]])", "expect": "[1, 4]"},
            {"call": "find_redundant_connection([[1, 2], [1, 3], [2, 3]])", "expect": "[2, 3]"},
        ],
        "approaches": {
            "For each edge, DFS to see if it is already connected": {
                "idea": [
                    "The graph is a tree plus one extra edge, so exactly one cycle exists, and the answer is the cycle edge that appears <strong>last</strong> in the input.",
                    "Adding edges in input order, the first edge whose endpoints are already connected is that edge: it is the one that completes the cycle.",
                ],
                "steps": [
                    "Start with an empty adjacency map <code>adj</code>.",
                    "For each edge <code>(a, b)</code>, run a DFS from <code>a</code> over the edges added so far, collecting <code>seen</code>.",
                    "If <code>b</code> is in <code>seen</code>, a path from a to b already exists, so this edge is redundant: return <code>[a, b]</code>.",
                    "Otherwise add the edge to <code>adj</code> in both directions and continue.",
                ],
                "why": [
                    "Before the cycle closes, the added edges form a forest; the first edge joining two already-connected nodes is exactly the last cycle edge in input order.",
                    "Removing it leaves the other edges, which form a spanning tree, as required.",
                    "Each of the n edges may trigger a DFS over up to n nodes: <strong>O(n²)</strong> time. The adjacency map and <code>seen</code> take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "(1,2): DFS from 1 sees {1}; 2 is not there. Add the edge.",
                        "(2,3): DFS from 2 sees {2, 1}. Add. (3,4): DFS from 3 sees {3, 2, 1}. Add.",
                        "(1,4): DFS from 1 goes 1 → 2 → 3 → 4, seen = {1, 2, 3, 4}.",
                        "4 is already reachable, so the result is <strong>[1, 4]</strong>; the edge (1, 5) is never examined.",
                    ],
                    [
                        "(1,2): DFS from 1 sees {1}. Add.",
                        "(1,3): DFS from 1 sees {1, 2}; 3 is not there. Add.",
                        "(2,3): DFS from 2 goes 2 → 1 → 3, seen = {2, 1, 3}.",
                        "3 is reachable: the result is <strong>[2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check before adding the edge, not after?",
                     "After adding it, a and b would always be connected through the edge itself, so every edge would look redundant."],
                    ["Why is the first redundant edge also the last cycle edge in the input?",
                     "All the other cycle edges come earlier and each joins two separate pieces. Only once they are all present can an edge find its endpoints already connected."],
                    ["Does the DFS start from <code>a</code> or <code>b</code>?",
                     "Either works; reachability is symmetric in an undirected graph."],
                ],
            },
            "Peel leaves until only the cycle remains": {
                "idea": [
                    "A node of degree 1 is a leaf and cannot be on a cycle, so remove it. Removing it can create new leaves; keep peeling.",
                    "When no leaves remain, the surviving nodes are exactly the cycle, and any edge with both ends on the cycle is a cycle edge.",
                    "The answer is the last such edge in the input, found by scanning <code>edges</code> backwards.",
                ],
                "steps": [
                    "Build <code>adj</code> as sets and compute <code>degree</code> for every node.",
                    "Seed a <code>queue</code> with every node of degree 1.",
                    "Pop a leaf <code>v</code>, add it to <code>removed</code>, and decrement the degree of each neighbour not yet removed; a neighbour that drops to 1 joins the queue.",
                    "When the queue empties, scan <code>reversed(edges)</code> and return the first <code>[a, b]</code> with neither end in <code>removed</code>.",
                ],
                "why": [
                    "Cycle nodes always keep two cycle neighbours, so their degree never falls to 1 and they are never peeled; every tree branch hanging off the cycle peels completely.",
                    "With one cycle, edges between two surviving nodes are exactly the cycle edges, so the backwards scan returns the last of them in the input.",
                    "Every node is peeled at most once and every edge scanned a constant number of times: <strong>O(n)</strong> time and <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Degrees: 1→3, 2→2, 3→2, 4→2, 5→1. queue = [5].",
                        "Pop 5: removed = {5}; degree[1] drops to 2, not a leaf. The queue is empty.",
                        "Surviving nodes: 1, 2, 3, 4, the cycle.",
                        "Backwards: [1, 5] touches 5, skip; [1, 4] has both ends alive: <strong>[1, 4]</strong>.",
                    ],
                    [
                        "Degrees: 1→2, 2→2, 3→2. No node has degree 1, so the queue starts empty.",
                        "Nothing is peeled: the whole graph is the triangle.",
                        "Backwards, the first edge is [2, 3], with both ends alive: <strong>[2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>degree[nb] == 1</code> instead of <code>&lt;= 1</code>?",
                     "Each node must enter the queue once. A neighbour is pushed at the moment its degree reaches 1; testing <code>&lt;= 1</code> could push it again if it later dropped to 0."],
                    ["Why scan the edges in reverse?",
                     "Several edges lie on the cycle and any of them could be removed; the problem asks for the one appearing last in the input."],
                    ["Does this work when the cycle has no tree branches?",
                     "Yes, as example 2 shows: the queue is empty from the start and every node survives."],
                ],
            },
            "Union-find: the first edge inside one set": {
                "idea": [
                    "Process edges in order, merging their endpoints' sets.",
                    "The first edge whose two endpoints are <strong>already in one set</strong> would close a cycle, and it is the answer.",
                ],
                "steps": [
                    "Create <code>parent = list(range(len(edges) + 1))</code>: nodes are labelled 1..n and there are n edges.",
                    "Define <code>find</code> with path halving.",
                    "For each edge <code>(a, b)</code>, compute <code>ra</code> and <code>rb</code>.",
                    "If <code>ra == rb</code>, return <code>[a, b]</code>.",
                    "Otherwise link <code>parent[ra] = rb</code> and continue.",
                ],
                "why": [
                    "Sets track exactly the connectivity of the edges already processed, the same thing the DFS version recomputes from scratch each time.",
                    "The first edge inside one set is the last cycle edge in input order, for the same reason as in the DFS approach.",
                    "Each edge costs two near-constant finds: <strong>O(n · α(n))</strong> time and <strong>O(n)</strong> space for <code>parent</code>.",
                ],
                "dry": [
                    [
                        "(1,2): roots 1, 2 → parent[1]=2. (2,3): parent[2]=3. (3,4): parent[3]=4.",
                        "(1,4): find(1) climbs 1 → 2 → 3 → 4, halving the path on the way. find(4)=4.",
                        "Both roots are 4, so the result is <strong>[1, 4]</strong>.",
                    ],
                    [
                        "(1,2): parent[1]=2.",
                        "(1,3): find(1)=2, find(3)=3 → parent[2]=3.",
                        "(2,3): find(2)=3 and find(3)=3, the same root: <strong>[2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why size <code>parent</code> as <code>len(edges) + 1</code>?",
                     "A tree on n nodes has n − 1 edges, so with one extra edge there are exactly n edges. Labels run 1..n, so index 0 is simply unused."],
                    ["Is the returned edge always the last cycle edge in the input?",
                     "Yes. Earlier cycle edges each joined two different sets, so the first failure is the edge that completes the cycle."],
                    ["How does this compare with the DFS version?",
                     "Same answer and logic, but each connectivity check costs near O(1) instead of a fresh O(n) traversal."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ accounts merge
    "accounts-merge": {
        "examples": [
            {"setup": "acc = [[\"John\", \"johnsmith@mail.com\", \"john_newyork@mail.com\"], [\"John\", \"johnsmith@mail.com\", \"john00@mail.com\"],\n       [\"Mary\", \"mary@mail.com\"], [\"John\", \"johnnybravo@mail.com\"]]",
             "call": "sorted(accounts_merge(acc))",
             "expect": "[[\"John\", \"john00@mail.com\", \"john_newyork@mail.com\", \"johnsmith@mail.com\"], [\"John\", \"johnnybravo@mail.com\"], [\"Mary\", \"mary@mail.com\"]]"},
            {"call": "sorted(accounts_merge([[\"A\", \"a1\", \"a2\"], [\"A\", \"a3\"], [\"A\", \"a2\", \"a3\"]]))",
             "expect": "[[\"A\", \"a1\", \"a2\", \"a3\"]]"},
        ],
        "approaches": {
            "Email graph, DFS per component": {
                "idea": [
                    "Treat each email as a node. Within one account, connect every email to that account's first email, a star that is enough to make the account connected.",
                    "Two accounts sharing an email then share a node, so each connected component is one merged person.",
                    "The name is not used for merging (two different Johns may exist); it is just looked up from <code>owner</code>.",
                ],
                "steps": [
                    "For each account, for each email <code>e</code>: set <code>owner[e] = name</code> and add an edge between <code>e</code> and <code>emails[0]</code> in <code>adj</code>.",
                    "Loop over the emails in <code>owner</code>; skip any already in <code>seen</code>.",
                    "From an unseen email, run an iterative DFS with <code>stack</code>, appending each popped email to <code>group</code>.",
                    "Append <code>[owner[e]] + sorted(group)</code> to <code>out</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "Emails of one account are connected by the star; a shared email links two stars, so components are exactly the transitive merges.",
                    "Every email is pushed once, so the traversal is linear; sorting each group dominates, giving <strong>O(N log N)</strong> time for N emails in total.",
                    "The graph, <code>owner</code> and <code>seen</code> hold O(1) entries per email: <strong>O(N)</strong> space.",
                ],
                "dry": [
                    [
                        "Edges: johnsmith–john_newyork (account 0) and johnsmith–john00 (account 1). mary and johnnybravo only link to themselves.",
                        "From johnsmith: pop it, push john_newyork and john00. Pop john00, then john_newyork.",
                        "Group sorted: john00, john_newyork, johnsmith (<code>'0'</code> sorts before <code>'_'</code>), owner John.",
                        "mary forms [Mary, mary], and johnnybravo forms [John, johnnybravo].",
                        "Sorted, the result is <strong>[[John, john00…, john_newyork…, johnsmith…], [John, johnnybravo…], [Mary, mary…]]</strong>.",
                    ],
                    [
                        "Edges: a1–a2 (account 0), a2–a3 (account 2, whose first email is a2). Account 1 adds only a3–a3.",
                        "From a1: pop a1, push a2. Pop a2, push a3. Pop a3: its neighbours are seen.",
                        "group = [a1, a2, a3], owner A.",
                        "Account 1 never shared an email directly with account 0 but is linked through account 2: <strong>[[A, a1, a2, a3]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why connect each email only to the first one, not all pairs?",
                     "A star already makes the account's emails one component, using k − 1 edges instead of k(k − 1)/2."],
                    ["Can I merge by name instead?",
                     "No. Example 1 has two separate Johns who share no email; merging by name would wrongly join them."],
                    ["Why the self-loops for single-email accounts?",
                     "The code adds the edge e–emails[0] even when they are equal. It is harmless (the node is already seen) and ensures the email appears in <code>owner</code>."],
                ],
            },
            "Union-find over account indices": {
                "idea": [
                    "Union accounts rather than emails: two accounts belong together when they share any email.",
                    "Remember the first account that listed each email in <code>first_owner</code>; when the email shows up again, union the current account with that one.",
                ],
                "steps": [
                    "Create <code>parent</code> over account indices 0..len(accounts)−1, with a path-halving <code>find</code>.",
                    "For account <code>i</code> and each email <code>e</code>: if <code>e</code> is in <code>first_owner</code>, set <code>parent[find(i)] = find(first_owner[e])</code>.",
                    "Otherwise record <code>first_owner[e] = i</code>.",
                    "Group emails by the root of their first owner: <code>groups[find(i)].append(e)</code>.",
                    "Return <code>[accounts[root][0]] + sorted(es)</code> for each group.",
                ],
                "why": [
                    "Every pair of accounts sharing an email is unioned, and union is transitive, so each set is exactly one person's accounts.",
                    "Every email lands in <code>first_owner</code> once, so each email appears in exactly one output group, with no duplicates.",
                    "Unions are near constant; sorting the groups costs <strong>O(N log N)</strong> for N emails. The maps and <code>parent</code> take <strong>O(N)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0: johnsmith→0, john_newyork→0.",
                        "i=1: johnsmith is already owned by 0, so parent[1]=0. john00→1.",
                        "i=2: mary→2. i=3: johnnybravo→3.",
                        "groups: root 0 gets johnsmith, john_newyork, john00 (find(1)=0); root 2 gets mary; root 3 gets johnnybravo.",
                        "Sorted, the result is <strong>[[John, john00…, john_newyork…, johnsmith…], [John, johnnybravo…], [Mary, mary…]]</strong>.",
                    ],
                    [
                        "i=0: a1→0, a2→0. i=1: a3→1.",
                        "i=2: a2 is owned by 0, so parent[2]=0. a3 is owned by 1: find(2)=0, so parent[0]=1.",
                        "parent = [1, 1, 0]: all three accounts share root 1.",
                        "groups {1: [a1, a2, a3]}; the name comes from accounts[1]: <strong>[[A, a1, a2, a3]]</strong>.",
                    ],
                ],
                "faq": [
                    ["The root in example 2 is account 1, not account 0. Does that matter?",
                     "No. All accounts in a set belong to one person, so they carry the same name; any of them can supply it."],
                    ["Why union with <code>first_owner[e]</code> and not every earlier owner?",
                     "Every earlier owner is already in the same set as the first one, so one union per repeated email is enough."],
                    ["Why <code>parent[find(i)]</code> rather than <code>parent[i]</code>?",
                     "Account <code>i</code> may already have been merged into another set by an earlier email. Linking its root keeps that set whole; overwriting <code>parent[i]</code> would split it."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ gcd traversal
    "gcd-traversal": {
        "examples": [
            {"call": "can_traverse_all_pairs([6, 10, 15, 35])", "expect": "True"},
            {"call": "can_traverse_all_pairs([3, 9, 5])", "expect": "False"},
        ],
        "approaches": {
            "Union every pair with gcd &gt; 1": {
                "idea": [
                    "Indices are nodes, and two indices are directly linked when their values share a factor (<code>gcd &gt; 1</code>).",
                    "Every pair can be traversed exactly when this graph is connected, so union all linked pairs and check for a single set.",
                ],
                "steps": [
                    "Create <code>parent = list(range(n))</code> and a path-halving <code>find</code>.",
                    "For every pair <code>i &lt; j</code>, compute <code>math.gcd(nums[i], nums[j])</code>.",
                    "If it exceeds 1, link <code>parent[find(i)] = find(j)</code>.",
                    "Return whether <code>{find(i) for i in range(n)}</code> has exactly one root.",
                ],
                "why": [
                    "Traversal is transitive, so i reaches j exactly when they lie in one component of the gcd graph, and union-find computes those components.",
                    "There are n(n − 1)/2 pairs and each gcd takes O(log max): <strong>O(n² log max)</strong> time.",
                    "Only <code>parent</code> is stored: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "(0,1): gcd(6,10)=2 → parent[0]=1. (0,2): gcd(6,15)=3 → parent[1]=2. (0,3): gcd(6,35)=1, skip.",
                        "(1,2): gcd 5, but both already have root 2.",
                        "(1,3): gcd(10,35)=5 → find(1)=2, parent[2]=3. (2,3): already joined.",
                        "Every index finds root 3, so the result is <strong>True</strong>.",
                    ],
                    [
                        "(0,1): gcd(3,9)=3 → parent[0]=1.",
                        "(0,2): gcd(3,5)=1 and (1,2): gcd(9,5)=1, both skipped.",
                        "Roots are {1, 2}: two components, so the result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["6 and 35 share no factor. Why is example 1 still True?",
                     "Traversal can go through other indices: 6 → 10 → 35 works because each step shares a factor (2, then 5)."],
                    ["What happens with a 1 in the array?",
                     "gcd(1, x) is always 1, so a 1 is never linked to anything and the answer is False unless the array is just <code>[1]</code>."],
                    ["Why is this too slow for the real constraints?",
                     "n can be 10<sup>5</sup>, making about 5·10<sup>9</sup> pairs. The factor-based approaches avoid comparing pairs at all."],
                ],
            },
            "Union each index with its prime factors": {
                "idea": [
                    "Two numbers share a factor exactly when they share a <strong>prime</strong> factor.",
                    "Add a node per prime and union each index with its primes. Indices sharing a prime then meet through that prime node, without comparing pairs.",
                ],
                "steps": [
                    "If <code>n == 1</code> return <code>True</code>; if any value is 1, return <code>False</code> (a 1 links to nothing).",
                    "Use a dictionary <code>parent</code>; <code>find</code> creates unseen keys on demand. Primes are keyed <code>(\"p\", p)</code> so they never clash with indices.",
                    "Factor each <code>v</code> by trial division: for each <code>p</code> with <code>p * p &lt;= v</code> that divides <code>v</code>, union the prime with index <code>i</code> and divide <code>p</code> out completely.",
                    "Whatever remains above 1 is one last large prime: union it with <code>i</code> too.",
                    "Return whether all indices share one root.",
                ],
                "why": [
                    "Index i and prime p are joined exactly when p divides nums[i], so two indices end up together exactly when a chain of shared primes connects them.",
                    "Trial division up to √v per value gives <strong>O(n √max)</strong> time.",
                    "Space is one entry per index plus one per distinct prime: <strong>O(n + primes)</strong>.",
                ],
                "dry": [
                    [
                        "6 = 2·3: primes 2 and 3 join index 0.",
                        "10 = 2·5: prime 2 is already with index 0, so index 1 joins that set; prime 5 joins too.",
                        "15 = 3·5: both primes are already in the set, so index 2 joins.",
                        "35 = 5·7: prime 5 brings index 3 in, and prime 7 joins. One root for all indices: <strong>True</strong>.",
                    ],
                    [
                        "3: the loop stops at once (4 &gt; 3); the leftover 3 joins index 0.",
                        "9: p=3 divides it, so prime 3 links index 1 with index 0; dividing leaves 1.",
                        "5: the leftover 5 joins index 2, a prime no one else has.",
                        "Indices 0, 1 and index 2 have different roots: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the <code>if v &gt; 1</code> after the loop?",
                     "Trial division stops at √v, so a prime factor larger than that (like 7 in 35, or 5 in 10) is left over and must still be unioned."],
                    ["Why tag primes as <code>(\"p\", p)</code>?",
                     "Index 3 and prime 3 are different things. A tuple key keeps the two kinds of node apart in one dictionary."],
                    ["Why is the special case for 1 needed?",
                     "1 has no prime factors, so its index would sit alone. Returning early is just faster and clearer; with n ≥ 2 it can never be connected."],
                ],
            },
            "Sieve of smallest prime factors, then union": {
                "idea": [
                    "Trial division repeats work across values. A sieve computes <code>spf[x]</code>, the smallest prime factor of every x ≤ max, once.",
                    "Then any value factors in O(log v) steps by repeatedly dividing by <code>spf[v]</code>; the union logic is the same as before.",
                ],
                "steps": [
                    "Handle <code>n == 1</code> (True) and any 1 in <code>nums</code> (False).",
                    "Build <code>spf = list(range(M + 1))</code>; for each prime <code>p ≤ √M</code>, set <code>spf[q] = p</code> for multiples <code>q</code> from p² that have no smaller factor yet.",
                    "Use a list <code>parent</code> of size <code>n + M + 1</code>: index i is node i, prime p is node <code>n + p</code>.",
                    "For each value, take <code>p = spf[v]</code>, union node <code>n + p</code> with i, divide p out completely, and repeat until <code>v == 1</code>.",
                    "Return whether every index has the same root as index 0.",
                ],
                "why": [
                    "The unions are exactly those of the trial-division approach, so the components and answer are the same.",
                    "The sieve costs O(M log log M); each value then has at most log₂ M prime-factor steps: <strong>O(M log log M + n log M)</strong> time.",
                    "The <code>spf</code> table and <code>parent</code> list are both sized by M: <strong>O(M)</strong> space.",
                ],
                "dry": [
                    [
                        "M = 35. The sieve gives spf[6]=2, spf[10]=2, spf[15]=3, spf[35]=5, spf[7]=7.",
                        "6: primes 2 and 3 (nodes 6 and 7) join index 0.",
                        "10: prime 2 brings index 1 in, then prime 5. 15: primes 3 and 5 bring index 2 in.",
                        "35: prime 5 brings index 3 in, then prime 7. All indices share a root: <strong>True</strong>.",
                    ],
                    [
                        "M = 9. The sieve sets spf[9]=3; 3 and 5 keep themselves.",
                        "3 → prime 3 (node 6) joins index 0. 9 → prime 3 links index 1 to it.",
                        "5 → prime 5 (node 8) joins index 2 alone.",
                        "find(2) differs from find(0): <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the sieve start each prime at p²?",
                     "Smaller multiples of p have a smaller prime factor and were already marked by that prime."],
                    ["Why the check <code>if spf[q] == q</code> before writing?",
                     "It keeps the <em>smallest</em> prime factor. Without it, a later larger prime would overwrite the value (e.g. spf[12] would become 3 instead of 2)."],
                    ["When is this better than trial division?",
                     "When n is large and values are bounded (say ≤ 10<sup>5</sup>): the sieve is paid once and each factorisation is then logarithmic instead of √v."],
                ],
            },
        },
    },
}
