"""Write-ups for the Union-Find topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ count connected components
    "count-connected-components": {
        "example": {"call": "count_components(6, [[0, 1], [1, 2], [3, 4], [2, 0]])", "expect": "3"},
        "approaches": {
            "DFS from every unvisited node": {
                "idea": [
                    "A connected component is everything reachable from one node.",
                    "Scan the nodes; each time an unvisited node turns up, it starts a new component, so flood it and mark everything reached.",
                    "The number of floods is the number of components.",
                ],
                "steps": [
                    "Build an adjacency list from the undirected edges (both directions).",
                    "For each node <code>start</code> not yet seen: <code>count += 1</code>, then DFS with an explicit stack, marking neighbours as seen.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Each flood marks one whole component, so later nodes of that component are skipped and nothing is counted twice.",
                    "Every node and edge is handled a constant number of times: O(V + E) time and space.",
                ],
                "dry": [
                    "Adjacency: 0→[1, 2], 1→[0, 2], 2→[1, 0], 3→[4], 4→[3], 5→[].",
                    "start=0: count = 1, and the flood reaches 1 and 2.",
                    "start=1 and start=2 are already seen, so they are skipped.",
                    "start=3: count = 2, and the flood reaches 4. start=4 is skipped.",
                    "start=5: count = 3; it has no neighbours.",
                    "The result is <strong>3</strong>.",
                ],
            },
            "Union-find, one decrement per successful union": {
                "idea": [
                    "Start with n separate components, one per node.",
                    "An edge between two <em>different</em> components merges them, which lowers the count by one. An edge inside one component changes nothing.",
                    "Union-find answers \"same component?\" in near O(1) and merges in near O(1), and it needs no adjacency list.",
                ],
                "steps": [
                    "<code>parent[x] = x</code>, <code>size[x] = 1</code>, <code>count = n</code>.",
                    "<code>find(x)</code> walks to the root, pointing each node at its grandparent on the way (path halving).",
                    "For each edge, find both roots. If they differ, hang the smaller tree under the larger and <code>count -= 1</code>.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Each successful union reduces the number of distinct roots by exactly one, so <code>count</code> always equals the number of components.",
                    "Union by size plus path halving make each operation O(α(V)), effectively constant: O(V + E·α(V)) time and O(V) space.",
                ],
                "dry": [
                    "Start with count = 6.",
                    "Edge (0, 1): roots 0 and 1 differ, so 1 goes under 0; size[0] = 2, count = 5.",
                    "Edge (1, 2): find(1) = 0 and find(2) = 2, so 2 goes under 0; size[0] = 3, count = 4.",
                    "Edge (3, 4): 4 goes under 3, count = 3.",
                    "Edge (2, 0): find(2) = 0 = find(0), the same root, so this edge closes a cycle and changes nothing.",
                    "The result is <strong>3</strong>: {0, 1, 2}, {3, 4} and {5}.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ graph valid tree
    "graph-valid-tree": {
        "example": {"call": "valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3]])", "expect": "False"},
        "approaches": {
            "Edge count, then DFS for connectivity": {
                "idea": [
                    "A graph on n nodes is a tree exactly when it has n - 1 edges <em>and</em> is connected.",
                    "Checking the edge count is O(1) and rejects most bad inputs.",
                    "If the count is right, one DFS from node 0 tells whether every node is reachable.",
                ],
                "steps": [
                    "If <code>len(edges) != n - 1</code>, return <code>False</code>.",
                    "Build the adjacency list.",
                    "DFS from 0 with a <code>seen</code> set.",
                    "Return <code>len(seen) == n</code>.",
                ],
                "why": [
                    "A connected graph with n - 1 edges cannot contain a cycle: removing a cycle edge would leave a connected graph with only n - 2 edges, which is impossible.",
                    "It is O(V + E) time and space.",
                ],
                "dry": [
                    "There are 4 edges and n - 1 = 4, so the count check passes.",
                    "Adjacency: 0→[1], 1→[0, 2, 3], 2→[1, 3], 3→[2, 1], 4→[].",
                    "DFS from 0 reaches 1, then 2 and 3. Node 4 is never reached.",
                    "seen = {0, 1, 2, 3} has 4 nodes, not 5, so the result is <strong>False</strong>. The cycle 1-2-3 \"used up\" the edge node 4 needed.",
                ],
            },
            "Edge count, then union-find for cycles": {
                "idea": [
                    "With exactly n - 1 edges, being a tree is the same as having no cycle.",
                    "Add edges one by one with union-find; an edge whose two ends already share a root would close a cycle.",
                    "If all n - 1 unions succeed, there is no cycle and everything has merged into one component.",
                ],
                "steps": [
                    "Reject unless there are n - 1 edges.",
                    "For each edge, find both roots; if they are equal, return <code>False</code>.",
                    "Otherwise link one root under the other.",
                    "Return <code>True</code> after all edges.",
                ],
                "why": [
                    "Each successful union merges two components, so n - 1 of them leave exactly one.",
                    "It is O(V + E·α(V)) time and O(V) space, and needs no adjacency list.",
                ],
                "dry": [
                    "Edge count: 4 = n - 1, so continue.",
                    "(0, 1): roots 0 and 1, link 0 under 1. (1, 2): roots 1 and 2, link 1 under 2.",
                    "(2, 3): roots 2 and 3, link 2 under 3.",
                    "(1, 3): find(1) walks 1 → 2 → 3, root 3; find(3) = 3. Same root, so this edge closes the cycle 1-2-3.",
                    "It returns <strong>False</strong> without even noticing that node 4 is isolated; the cycle alone is enough.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ redundant connection
    "redundant-connection": {
        "example": {"call": "find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]])", "expect": "[1, 4]"},
        "approaches": {
            "For each edge, DFS to see if it is already connected": {
                "idea": [
                    "Build the graph edge by edge, in input order.",
                    "Before adding (a, b), ask whether a can already reach b; if it can, this edge would close a cycle.",
                    "The input is a tree plus one edge, so the first such edge is the answer.",
                ],
                "steps": [
                    "Keep an adjacency list of the edges added so far.",
                    "For each <code>(a, b)</code>: DFS from <code>a</code>; if <code>b</code> was reached, return <code>[a, b]</code>.",
                    "Otherwise add the edge in both directions.",
                ],
                "why": [
                    "An edge closes a cycle exactly when its ends are already connected.",
                    "Every other edge on the cycle was added earlier, so the first cycle-closing edge is also the last cycle edge in the input, which is the tie-break the problem asks for.",
                    "There are up to n DFS runs of O(n) each: O(n²) time and O(n) space.",
                ],
                "dry": [
                    "Edge (1, 2): the DFS from 1 sees only {1}, so add it.",
                    "Edge (2, 3): the DFS from 2 sees {1, 2}, so add it.",
                    "Edge (3, 4): the DFS from 3 sees {1, 2, 3}, so add it.",
                    "Edge (1, 4): the DFS from 1 reaches 2, 3, 4. Since 4 is reachable, return <strong>[1, 4]</strong>.",
                ],
            },
            "Peel leaves until only the cycle remains": {
                "idea": [
                    "A node with degree 1 cannot be on a cycle, so remove it. That may turn its neighbour into a new leaf.",
                    "Keep peeling leaves (like a topological sort); because the graph is a tree plus one edge, what survives is exactly the cycle.",
                    "The answer is the cycle edge that appears last in the input.",
                ],
                "steps": [
                    "Build adjacency sets and degrees for the whole graph.",
                    "Queue every degree-1 node. Pop one, mark it removed, and lower each remaining neighbour's degree; queue any neighbour that drops to 1.",
                    "Scan the edges backwards and return the first one with both ends still present.",
                ],
                "why": [
                    "Peeling never removes a cycle node, because a cycle node always keeps two cycle neighbours.",
                    "Each node and edge is processed once: O(n) time and space. Unlike DSU, it needs the whole graph up front.",
                ],
                "dry": [
                    "Degrees: 1→3 (neighbours 2, 4, 5), 2→2, 3→2, 4→2, 5→1.",
                    "The queue starts with [5]. Remove 5; node 1's degree drops to 2, not a leaf.",
                    "The queue is empty, and nodes 1, 2, 3, 4 remain: the cycle.",
                    "Scanning edges from the end: (1, 5) has 5 removed, skip; (1, 4) has both ends remaining, return <strong>[1, 4]</strong>.",
                ],
            },
            "Union-find: the first edge inside one set": {
                "idea": [
                    "Union edges in input order.",
                    "The first edge whose endpoints already have the same root lies on the cycle, and since the other cycle edges came before it, it is the last one.",
                ],
                "steps": [
                    "<code>parent = list(range(n + 1))</code>, because nodes are numbered from 1.",
                    "For each <code>(a, b)</code>: if <code>find(a) == find(b)</code>, return <code>[a, b]</code>.",
                    "Otherwise set <code>parent[find(a)] = find(b)</code>.",
                ],
                "why": [
                    "Same roots means already connected, so this edge closes the cycle.",
                    "It takes O(n·α(n)) time and O(n) space, and processes edges as they arrive.",
                ],
                "dry": [
                    "(1, 2): link 1 under 2. (2, 3): link 2 under 3. (3, 4): link 3 under 4.",
                    "(1, 4): find(1) walks 1 → 2 → 3 → 4, compressing as it goes, so the root is 4. find(4) = 4.",
                    "The roots are equal, so return <strong>[1, 4]</strong>. Edge (1, 5) is never looked at.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ accounts merge
    "accounts-merge": {
        "example": {"setup": 'acc = [["John", "johnsmith@mail.com", "john_newyork@mail.com"], ["John", "johnsmith@mail.com", "john00@mail.com"],\n       ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]]',
                    "call": "sorted(accounts_merge(acc))",
                    "expect": '[["John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"], ["John", "johnnybravo@mail.com"], ["Mary", "mary@mail.com"]]'},
        "approaches": {
            "Email graph, DFS per component": {
                "idea": [
                    "Two accounts belong to one person if they share an email, and that relation chains: A shares with B, B with C.",
                    "Make each email a node and connect every email of an account to that account's first email, so each account becomes a star.",
                    "Each connected component of this graph is one person's email set.",
                ],
                "steps": [
                    "For each account, record <code>owner[e] = name</code> and add edges between <code>emails[0]</code> and every email <code>e</code>.",
                    "For each email not yet seen, DFS to collect its whole component.",
                    "Output <code>[owner] + sorted(group)</code> per component.",
                ],
                "why": [
                    "Shared emails become shared nodes, so accounts linked through any chain end up in one component.",
                    "With N total emails, the graph is O(N) and sorting dominates: O(N log N) time, O(N) space.",
                ],
                "dry": [
                    "Account 0 links johnsmith with john_newyork. Account 1 links johnsmith with john00, joining the same star.",
                    "Mary's and Johnny Bravo's accounts stay alone.",
                    "The DFS from johnsmith collects {johnsmith, john_newyork, john00}, which sorts to john00, john_newyork, johnsmith.",
                    "The DFS from mary collects {mary}, and the one from johnnybravo collects {johnnybravo}.",
                    "Sorted, the output is <strong>[[John, john00, john_newyork, johnsmith], [John, johnnybravo], [Mary, mary]]</strong>.",
                ],
            },
            "Union-find over account indices": {
                "idea": [
                    "Merge <em>accounts</em> rather than emails: one union-find node per account keeps the structure small.",
                    "Remember which account first listed each email. When a later account lists the same email, union the two accounts.",
                    "At the end, group every email under its account's root.",
                ],
                "steps": [
                    "<code>first_owner[e]</code> is the index of the first account containing <code>e</code>.",
                    "For each later sighting of <code>e</code> in account <code>i</code>: <code>parent[find(i)] = find(first_owner[e])</code>.",
                    "Group emails by <code>find(first_owner[e])</code>, then emit the root account's name with the sorted emails.",
                ],
                "why": [
                    "Any chain of shared emails produces a chain of unions, so the accounts of one person share a root.",
                    "There are N email lookups plus near-constant unions, and sorting dominates: O(N log N) time, O(N) space.",
                ],
                "dry": [
                    "Account 0: johnsmith→0 and john_newyork→0.",
                    "Account 1: johnsmith already belongs to 0, so union 1 under 0; john00→1.",
                    "Account 2: mary→2. Account 3: johnnybravo→3.",
                    "Grouping by root: root 0 gets johnsmith, john_newyork and john00 (via account 1); root 2 gets mary; root 3 gets johnnybravo.",
                    "Sorted, the output is <strong>[[John, john00, john_newyork, johnsmith], [John, johnnybravo], [Mary, mary]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ gcd traversal
    "gcd-traversal": {
        "example": {"call": "can_traverse_all_pairs([6, 10, 15, 35])", "expect": "True"},
        "approaches": {
            "Union every pair with gcd &gt; 1": {
                "idea": [
                    "Indices i and j are directly linked when their numbers share a factor, meaning <code>gcd &gt; 1</code>.",
                    "Every pair is reachable exactly when that link graph is connected.",
                    "So test every pair, union the linked ones, and check that one set remains.",
                ],
                "steps": [
                    "For each pair <code>i &lt; j</code>, compute <code>gcd(nums[i], nums[j])</code>.",
                    "If it is greater than 1, union i and j.",
                    "Return whether all indices share a root.",
                ],
                "why": [
                    "It builds exactly the problem's graph, so it is correct.",
                    "There are n²/2 gcd calls of O(log max) each: hopeless for n = 10<sup>5</sup>, fine for tiny inputs.",
                ],
                "dry": [
                    "(6, 10): gcd 2, union. (6, 15): gcd 3, union. (6, 35): gcd 1, no link.",
                    "(10, 15): gcd 5, already joined. (10, 35): gcd 5, union index 3 into the set.",
                    "(15, 35): gcd 5, already joined.",
                    "All four indices share one root, so the result is <strong>True</strong>, even though 6 and 35 share no factor directly.",
                ],
            },
            "Union each index with its prime factors": {
                "idea": [
                    "Two numbers share a factor exactly when they share a <em>prime</em> factor.",
                    "So add a node for each prime and connect each index to its primes. Indices that share a prime become connected through that prime's node.",
                    "This replaces n² pair tests with factoring each number once.",
                ],
                "steps": [
                    "A single number is trivially fine; any 1 (when n &gt; 1) shares no factor with anything, so return <code>False</code>.",
                    "Trial-divide each value by p = 2, 3, ... up to √v; for each prime p that divides it, union index i with node <code>(\"p\", p)</code>.",
                    "Whatever remains above 1 is a prime factor too.",
                    "Check that all indices share one root.",
                ],
                "why": [
                    "Paths through prime nodes match paths in the original gcd graph, so connectivity is preserved.",
                    "Factoring costs O(√max) per number, with only a handful of unions each: O(n√max) time.",
                ],
                "dry": [
                    "6 = 2 × 3: link index 0 with p2 and p3.",
                    "10 = 2 × 5: p2 already belongs to index 0's set, so index 1 joins it; p5 joins too.",
                    "15 = 3 × 5: index 2 joins through p3 (and p5).",
                    "35 = 5 × 7: index 3 joins through p5; p7 comes along.",
                    "All indices share a root, so the result is <strong>True</strong>.",
                ],
            },
            "Sieve of smallest prime factors, then union": {
                "idea": [
                    "Trial division repeats work across numbers. Instead, precompute the smallest prime factor (spf) of every value up to the maximum.",
                    "Then any number factors in O(log M) by repeatedly dividing by its spf.",
                    "The union step is the same as before: connect each index with its prime nodes, offset by n so they do not clash with indices.",
                ],
                "steps": [
                    "Sieve: for each prime p up to √M, set <code>spf[q] = p</code> for multiples q not yet marked.",
                    "For each value: <code>p = spf[v]</code>, union index i with <code>n + p</code>, divide p out, and repeat until v is 1.",
                    "Return whether every index has the same root as index 0.",
                ],
                "why": [
                    "spf factoring yields exactly the distinct primes of each number.",
                    "The sieve is O(M log log M) once, and each number then factors in O(log M): O(M log log M + n log M) time, O(M) space.",
                ],
                "dry": [
                    "M = 35. The sieve gives, for example, spf[6] = 2, spf[15] = 3, spf[35] = 5, spf[7] = 7.",
                    "6: spf 2, union with node n+2; v becomes 3, spf 3, union with n+3.",
                    "10: primes 2 then 5, so it joins index 0 through n+2.",
                    "15: primes 3 then 5. 35: primes 5 then 7, joining through n+5.",
                    "Every index has the same root as index 0, so the result is <strong>True</strong>.",
                ],
            },
        },
    },
}
