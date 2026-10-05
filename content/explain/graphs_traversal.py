"""Write-ups for the Graphs topic, part 1: traversal problems."""

CLONE_SETUP = ("class Node:\n"
               "    def __init__(self, val=0, neighbors=None):\n"
               "        self.val = val\n"
               "        self.neighbors = neighbors if neighbors is not None else []\n"
               "n1, n2, n3, n4 = Node(1), Node(2), Node(3), Node(4)      # a square: 1-2-3-4-1\n"
               "n1.neighbors, n2.neighbors, n3.neighbors, n4.neighbors = [n2, n4], [n1, n3], [n2, n4], [n1, n3]\n"
               "originals = {n1, n2, n3, n4}\n"
               "def dump(start):                       # (value, neighbour values, is an original node?)\n"
               "    seen, stack, out = {start}, [start], []\n"
               "    while stack:\n"
               "        x = stack.pop()\n"
               "        out.append((x.val, sorted(y.val for y in x.neighbors), x in originals))\n"
               "        for y in x.neighbors:\n"
               "            if y not in seen:\n"
               "                seen.add(y)\n"
               "                stack.append(y)\n"
               "    return sorted(out)\n"
               "copy = clone_graph(n1)")

EXPLAIN = {
    # ------------------------------------------------------------------ island perimeter
    "island-perimeter": {
        "example": {"call": "island_perimeter([[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [1, 1, 0, 0]])", "expect": "16"},
        "approaches": {
            "DFS, counting edges that face water or the border": {
                "idea": [
                    "The perimeter is made of cell edges where land meets water or the edge of the grid.",
                    "Flood the island from any land cell and, for each land cell, count the sides that step into water or off the grid.",
                ],
                "steps": [
                    "Find a land cell; DFS with a <code>seen</code> set.",
                    "For each of the 4 directions: water or off-grid adds 1; unseen land is pushed.",
                ],
                "why": [
                    "Each perimeter edge is counted from the one land cell it belongs to.",
                    "It is O(m·n). It is overkill here, but it extends to \"the perimeter of the island containing cell X\".",
                ],
                "dry": [
                    "The island has 7 land cells.",
                    "Counting the water or border sides of each cell gives 3, 3, 3, 2, 3, 1 and 1 (in some order).",
                    "The total is <strong>16</strong>.",
                ],
            },
            "Count lands and shared edges": {
                "idea": [
                    "Each land cell brings 4 edges; every pair of adjacent land cells hides 2 of them (one side from each cell).",
                    "So the perimeter is <code>4 × lands - 2 × shared</code>.",
                    "Counting only each cell's right and down neighbour counts every adjacent pair exactly once.",
                ],
                "steps": [
                    "Scan the cells; for each land cell, add 1 to lands and check its right and down neighbours.",
                    "Return <code>4·lands - 2·shared</code>.",
                ],
                "why": [
                    "There is no traversal and no visited set: O(m·n) time and O(1) space.",
                ],
                "dry": [
                    "lands = 1 + 3 + 1 + 2 = 7.",
                    "shared pairs: (0,1)-(1,1), (1,0)-(1,1), (1,1)-(1,2), (1,1)-(2,1), (2,1)-(3,1), (3,0)-(3,1). That is 6.",
                    "4·7 - 2·6 = <strong>16</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ verify alien dictionary
    "verify-alien-dictionary": {
        "example": {"call": 'is_alien_sorted(["word", "world", "row"], "worldabcefghijkmnpqstuvxyz")', "expect": "False"},
        "approaches": {
            "Translate to English letters, compare with sorted": {
                "idea": [
                    "Map each alien letter to the English letter with the same rank, then normal string order is alien order.",
                    "Translate every word and check that the list equals its sorted version.",
                ],
                "steps": [
                    "<code>to_english[order[i]] = chr(97 + i)</code>.",
                    "Translate the words; compare the list with <code>sorted(...)</code>.",
                ],
                "why": [
                    "Python's string comparison handles the prefix rule automatically. It is O(C log n) for C characters.",
                ],
                "dry": [
                    "w→a, o→b, r→c, l→d, d→e.",
                    "\"word\" becomes \"abce\", \"world\" becomes \"abcde\", \"row\" becomes \"cba\".",
                    "Sorted, it would be [\"abcde\", \"abce\", \"cba\"], which differs, so the result is <strong>False</strong>.",
                ],
            },
            "Rank map, compare adjacent pairs": {
                "idea": [
                    "A list is sorted exactly when each adjacent pair is in order.",
                    "Compare each pair at the first differing letter using the alien rank; if no letter differs, the longer word must come second.",
                ],
                "steps": [
                    "<code>rank[ch] = i</code>.",
                    "For each pair: at the first difference, return <code>False</code> if the ranks are out of order; if one is a prefix of the other, the first must not be longer.",
                ],
                "why": [
                    "It is O(C) and stops at the first violation.",
                ],
                "dry": [
                    "\"word\" vs \"world\": w, o, r match; then d vs l.",
                    "rank[d] = 4 &gt; rank[l] = 3, so \"word\" should come after \"world\".",
                    "The result is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find the town judge
    "find-town-judge": {
        "example": {"call": "find_judge(4, [[1, 3], [1, 4], [2, 3], [2, 4], [4, 3]])", "expect": "3"},
        "approaches": {
            "Check each candidate against all trust pairs": {
                "idea": [
                    "The judge trusts nobody and is trusted by everyone else.",
                    "Test each person against the full trust list.",
                ],
                "steps": [
                    "Skip anyone who appears as a truster.",
                    "Return a person trusted exactly n - 1 times.",
                ],
                "why": [
                    "It is O(n·t).",
                ],
                "dry": [
                    "Persons 1, 2 and 4 each trust someone, so they are ruled out.",
                    "Person 3 trusts nobody and is trusted by 1, 2 and 4, which is 3 = n - 1.",
                    "The result is <strong>3</strong>.",
                ],
            },
            "In-degree and out-degree arrays": {
                "idea": [
                    "Treat trust as directed edges. The judge has out-degree 0 and in-degree n - 1.",
                ],
                "steps": [
                    "Count both degrees in one pass over the edges.",
                    "Find the person with out 0 and in n - 1.",
                ],
                "why": [
                    "It is O(n + t) time and O(n) space.",
                ],
                "dry": [
                    "out: 1→2, 2→2, 4→1. in: 3→3, 4→2.",
                    "Person 3 has out 0 and in 3, so the result is <strong>3</strong>.",
                ],
            },
            "One net-trust score": {
                "idea": [
                    "Combine both degrees into one score: +1 for being trusted, -1 for trusting.",
                    "Only the judge can reach n - 1: that needs every possible incoming trust and no outgoing ones.",
                ],
                "steps": [
                    "<code>score[a] -= 1</code>, <code>score[b] += 1</code> for each edge.",
                    "Return the person with score n - 1.",
                ],
                "why": [
                    "Anyone who trusts someone loses at least 1 and cannot reach the maximum.",
                ],
                "dry": [
                    "Scores: 1 → -2, 2 → -2, 3 → +3, 4 → +2 - 1 = +1.",
                    "Only person 3 reaches 3: <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ number of islands
    "number-of-islands": {
        "example": {"setup": 'g = [list("11000"), list("11000"), list("00100"), list("00011")]',
                    "call": "num_islands(g)", "expect": "3"},
        "approaches": {
            "Recursive DFS, sinking visited land": {
                "idea": [
                    "Scan the grid. Each time you hit land that has not been visited, that is a new island.",
                    "Recursively turn that whole island to water (sink it) so it is never counted again.",
                ],
                "steps": [
                    "Copy the grid.",
                    "On a '1': count it, then <code>sink</code> it, recursing in 4 directions.",
                ],
                "why": [
                    "Each land cell is sunk exactly once: O(m·n), but the recursion depth can reach m·n.",
                ],
                "dry": [
                    "(0, 0) is land: count 1, and sink the 2×2 block.",
                    "(2, 2) is land: count 2, a single cell.",
                    "(3, 3) is land: count 3, and sink it together with (3, 4).",
                    "The result is <strong>3</strong>.",
                ],
            },
            "Iterative BFS with a visited set": {
                "idea": [
                    "The same scan, flooding each island with a queue instead of recursion.",
                    "Mark cells as seen when they are enqueued, so no cell enters the queue twice.",
                ],
                "steps": [
                    "On unvisited land: count it, then BFS through its land neighbours.",
                ],
                "why": [
                    "It is O(m·n), has no recursion limit, and does not modify the input.",
                ],
                "dry": [
                    "BFS from (0, 0) reaches (1, 0), (0, 1) and (1, 1): island 1.",
                    "(2, 2) alone is island 2. BFS from (3, 3) reaches (3, 4): island 3.",
                    "The result is <strong>3</strong>.",
                ],
            },
            "Union-find over land cells": {
                "idea": [
                    "Start with every land cell as its own island.",
                    "Union each land cell with its land neighbours to the right and below; every successful union merges two islands into one.",
                ],
                "steps": [
                    "<code>count</code> = the number of land cells.",
                    "For each land cell and each right or down land neighbour: if their roots differ, union them and <code>count -= 1</code>.",
                ],
                "why": [
                    "It is O(m·n·α), and it extends to adding land one cell at a time (Number of Islands II).",
                ],
                "dry": [
                    "There are 7 land cells, so count starts at 7.",
                    "The 2×2 block: three successful unions, and the fourth pair is already joined. Count 4.",
                    "(3, 3) with (3, 4): count 3.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max area of island
    "max-area-of-island": {
        "example": {"call": "max_area_of_island([[1, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1]])", "expect": "6"},
        "approaches": {
            "Recursive DFS returning the area": {
                "idea": [
                    "<code>area(r, c)</code> is 1 plus the areas reached through its four neighbours, and 0 for water, off-grid or visited cells.",
                    "Marking a cell visited before recursing prevents double counting.",
                ],
                "steps": [
                    "Return the max of <code>area(r, c)</code> over all cells.",
                ],
                "why": [
                    "It is O(m·n), with recursion depth up to m·n.",
                ],
                "dry": [
                    "area(0, 0) = 1 + area(1, 0) + area(0, 1) = 3.",
                    "area(1, 3) floods (2, 3), (2, 2), (3, 2), (3, 3), (3, 1), giving 6.",
                    "The maximum is <strong>6</strong>.",
                ],
            },
            "Iterative flood fill with a stack": {
                "idea": [
                    "The same flood with an explicit stack, counting cells as they are popped.",
                ],
                "steps": [
                    "For each unvisited land cell, flood it and track the size.",
                ],
                "why": [
                    "It is O(m·n) and safe for any grid size.",
                ],
                "dry": [
                    "The flood from (0, 0) pops 3 cells. The flood from (1, 3) pops 6 cells.",
                    "The best is <strong>6</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ clone graph
    "clone-graph": {
        "example": {"setup": CLONE_SETUP, "call": "dump(copy)",
                    "expect": "[(1, [2, 4], False), (2, [1, 3], False), (3, [2, 4], False), (4, [1, 3], False)]"},
        "approaches": {
            "DFS with an original &rarr; copy map": {
                "idea": [
                    "<code>clone(n)</code> returns the existing copy of n if there is one; otherwise it makes the copy, records it first, then clones the neighbours.",
                    "Recording before recursing is what stops cycles: a neighbour that leads back finds the copy already there.",
                ],
                "steps": [
                    "<code>copies[n] = Node(n.val)</code>.",
                    "<code>c.neighbors = [clone(nb) for nb in n.neighbors]</code>.",
                ],
                "why": [
                    "Every node and edge is visited once: O(V + E).",
                ],
                "dry": [
                    "clone(1) creates 1', then clones 2: 2' is created, and its first neighbour 1 is already in the map.",
                    "2' then clones 3: 3' is created; its neighbours 2 and 4 lead to the existing 2' and a new 4', whose neighbours 1 and 3 are both copied already.",
                    "The square is rebuilt from new nodes only.",
                    "dump gives <strong>[(1, [2, 4], False), (2, [1, 3], False), (3, [2, 4], False), (4, [1, 3], False)]</strong>.",
                ],
            },
            "BFS with an original &rarr; copy map": {
                "idea": [
                    "Copy the start node and enqueue the original.",
                    "For each dequeued node, copy any neighbour not seen yet (and enqueue it), then append the neighbour's copy to the current copy's list.",
                ],
                "steps": [
                    "<code>copies = {node: Node(node.val)}</code>.",
                    "Pop n; for each nb: create its copy if needed, then <code>copies[n].neighbors.append(copies[nb])</code>.",
                ],
                "why": [
                    "It is iterative, so there are no recursion limits: O(V + E).",
                ],
                "dry": [
                    "Pop 1: create 2' and 4', so 1' → [2', 4'].",
                    "Pop 2: 1' already exists; create 3'. 2' → [1', 3'].",
                    "Pop 4: 4' → [1', 3']. Pop 3: 3' → [2', 4'].",
                    "dump gives <strong>[(1, [2, 4], False), (2, [1, 3], False), (3, [2, 4], False), (4, [1, 3], False)]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ walls and gates
    "walls-and-gates": {
        "example": {"setup": "INF = 2147483647\nR = [[INF, -1, 0, INF], [INF, INF, INF, -1], [INF, -1, INF, -1], [0, -1, INF, INF]]\nwalls_and_gates(R)",
                    "call": "R", "expect": "[[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]"},
        "approaches": {
            "BFS from every empty room": {
                "idea": [
                    "For each empty room, BFS outward until the first gate; its level is the distance.",
                ],
                "steps": [
                    "Keep the original grid for reading; for each INF cell, BFS until a 0.",
                ],
                "why": [
                    "Each BFS can cover the whole grid, and there are up to m·n rooms: O((m·n)²).",
                ],
                "dry": [
                    "Room (0, 0): BFS reaches the gate at (3, 0) in 3 steps, so 3.",
                    "Room (3, 3): the nearest gate is 4 steps away, so 4.",
                    "Every room gets its own search. The result is <strong>[[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]</strong>.",
                ],
            },
            "Multi-source BFS from all gates at once": {
                "idea": [
                    "Put every gate in the queue at distance 0 and run a single BFS.",
                    "BFS reaches cells in order of distance, and all gates start together, so the first time a room is reached it is from its nearest gate.",
                    "Writing the distance into the room also marks it as visited.",
                ],
                "steps": [
                    "Queue all gates.",
                    "Pop a cell; each INF neighbour gets the cell's value + 1 and is queued.",
                ],
                "why": [
                    "Every cell enters the queue at most once: O(m·n), however many gates there are.",
                ],
                "dry": [
                    "The gates are (0, 2) and (3, 0).",
                    "Distance 1: (0, 3), (1, 2), (2, 0). Distance 2: (1, 1), (2, 2), (1, 0).",
                    "Distance 3: (0, 0), (3, 2). Distance 4: (3, 3).",
                    "The result is <strong>[[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ rotting oranges
    "rotting-oranges": {
        "example": {"call": "oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]])", "expect": "4"},
        "approaches": {
            "Simulate minute by minute": {
                "idea": [
                    "Each minute, find every fresh orange next to a rotten one, and rot them all at once.",
                    "Collect the list before applying it, so newly rotten oranges do not spread in the same minute.",
                    "Stop when nothing changes; any fresh orange left means -1.",
                ],
                "steps": [
                    "Repeat: collect the oranges to rot; if there are none, stop; otherwise rot them and add a minute.",
                ],
                "why": [
                    "It can take up to m·n minutes of O(m·n) scans.",
                ],
                "dry": [
                    "Minute 1: (0, 1) and (1, 0). Minute 2: (0, 2) and (1, 1).",
                    "Minute 3: (2, 1). Minute 4: (2, 2).",
                    "No fresh oranges remain, so the result is <strong>4</strong>.",
                ],
            },
            "Multi-source BFS by levels": {
                "idea": [
                    "Start the queue with every rotten orange; each BFS level is one minute.",
                    "Count the fresh oranges up front, and decrement as they rot.",
                ],
                "steps": [
                    "While the queue is non-empty and fresh oranges remain: process one level, rotting fresh neighbours, then add a minute.",
                    "Return -1 if any fresh oranges remain.",
                ],
                "why": [
                    "Each cell is processed once: O(m·n).",
                ],
                "dry": [
                    "Level 0: (0, 0). Level 1: (0, 1), (1, 0). Level 2: (0, 2), (1, 1).",
                    "Level 3: (2, 1). Level 4: (2, 2), and the fresh count hits 0.",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ pacific atlantic
    "pacific-atlantic": {
        "example": {"call": "sorted(pacific_atlantic([[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]))",
                    "expect": "[[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]"},
        "approaches": {
            "DFS from every cell": {
                "idea": [
                    "From each cell, explore downhill (to neighbours at the same height or lower) and record which oceans the water reaches.",
                ],
                "steps": [
                    "For each cell, DFS while tracking the Pacific (top or left edge) and the Atlantic (bottom or right edge); stop once both are seen.",
                ],
                "why": [
                    "Each search can cover the grid: O((m·n)²).",
                ],
                "dry": [
                    "From (2, 2), height 5, water flows to both oceans.",
                    "From (1, 1), height 2, it reaches the Pacific but is boxed in from the Atlantic.",
                    "Seven cells reach both: <strong>[[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]</strong>.",
                ],
            },
            "Reverse flow: search uphill from each ocean": {
                "idea": [
                    "Instead of asking where water from each cell goes, ask which cells each ocean can be reached from.",
                    "Start from all the ocean's edge cells and move <em>uphill</em> (to neighbours at least as high): every cell reached can drain to that ocean.",
                    "Do this once for each ocean; the answer is the cells reached by both.",
                ],
                "steps": [
                    "<code>reach(starts)</code>: a multi-source DFS with the ≥ rule.",
                    "Return the sorted intersection.",
                ],
                "why": [
                    "Each cell is visited at most twice: O(m·n).",
                ],
                "dry": [
                    "The Pacific search starts from row 0 and column 0 and climbs inward.",
                    "The Atlantic search starts from row 4 and column 4.",
                    "Their intersection is <strong>[[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ surrounded regions
    "surrounded-regions": {
        "example": {"setup": 'B = [list("XXXX"), list("XOOX"), list("XXOX"), list("XOXX")]\nsolve(B)',
                    "call": "B", "expect": '[["X", "X", "X", "X"], ["X", "X", "X", "X"], ["X", "X", "X", "X"], ["X", "O", "X", "X"]]'},
        "approaches": {
            "Explore each region, flip if it never touches the border": {
                "idea": [
                    "An 'O' region is captured exactly when none of its cells touches the border.",
                    "Flood each region, remember whether any cell is on the border, and flip it if not.",
                ],
                "steps": [
                    "For each unvisited 'O': collect its region and a <code>border</code> flag.",
                    "If <code>border</code> is false, set every cell in the region to 'X'.",
                ],
                "why": [
                    "Each cell is visited once: O(m·n).",
                ],
                "dry": [
                    "The region {(1, 1), (1, 2), (2, 2)} touches no border, so flip it.",
                    "The region {(3, 1)} is on the bottom edge, so it stays 'O'.",
                    "The result is <strong>[[X, X, X, X], [X, X, X, X], [X, X, X, X], [X, O, X, X]]</strong>.",
                ],
            },
            "Mark safe cells from the border, then flip": {
                "idea": [
                    "Turn the question around: the 'O's that survive are those connected to a border 'O'.",
                    "Flood from every border 'O', temporarily marking cells 'S' (safe).",
                    "Then one sweep: any 'O' left was surrounded, so it becomes 'X'; every 'S' goes back to 'O'.",
                ],
                "steps": [
                    "Push every border 'O'; pop cells, marking 'O' as 'S' and pushing neighbours.",
                    "Sweep the board, mapping 'S' to 'O' and everything else to 'X'.",
                ],
                "why": [
                    "The marks live in the board itself, so no visited set is needed: O(m·n).",
                ],
                "dry": [
                    "The only border 'O' is (3, 1), marked 'S'; its neighbours are all 'X'.",
                    "Sweep: (1, 1), (1, 2) and (2, 2) are still 'O', so they become 'X'; (3, 1) goes back to 'O'.",
                    "The result is <strong>[[X, X, X, X], [X, X, X, X], [X, X, X, X], [X, O, X, X]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ open the lock
    "open-the-lock": {
        "example": {"call": 'open_lock(["0201", "0101", "0102", "1212", "2002"], "0202")', "expect": "6"},
        "approaches": {
            "BFS from the start": {
                "idea": [
                    "Each lock state is a node; one wheel turn up or down is an edge, giving 8 neighbours per state.",
                    "The fewest turns is a shortest path in an unweighted graph, so BFS from \"0000\", skipping dead ends.",
                ],
                "steps": [
                    "Queue <code>(\"0000\", 0)</code>; for each state, generate its 8 neighbours and enqueue the unseen, non-dead ones.",
                    "Return the level at which the target is dequeued.",
                ],
                "why": [
                    "BFS explores states in order of turn count. There are at most 10<sup>4</sup> states with 8 edges each.",
                ],
                "dry": [
                    "The direct routes to \"0202\" through \"0201\" or \"0102\" are dead ends.",
                    "One shortest route: 0000 → 1000 → 1100 → 1200 → 1201 → 1202 → 0202.",
                    "BFS first reaches the target at level <strong>6</strong>.",
                ],
            },
            "Bidirectional BFS": {
                "idea": [
                    "Grow one frontier from the start and one from the target, always expanding the smaller one, until they touch.",
                    "Each side then only needs to search about half the distance, which is far fewer states.",
                ],
                "steps": [
                    "Keep the sets <code>front</code> and <code>back</code>; swap them if front is bigger.",
                    "Expand front by one level; if a neighbour is in back, return the move count.",
                ],
                "why": [
                    "It explores about b<sup>d/2</sup> states per side instead of b<sup>d</sup>, the standard speed-up for shortest-path puzzles.",
                ],
                "dry": [
                    "The two searches expand alternately from \"0000\" and \"0202\".",
                    "They meet in the middle of a 6-turn route.",
                    "The result is <strong>6</strong>.",
                ],
            },
        },
    },
}
