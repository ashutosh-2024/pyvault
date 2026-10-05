"""Write-ups for the Backtracking topic."""

ROBOT = ("class Robot:\n"
         "    STEP = [(-1, 0), (0, 1), (1, 0), (0, -1)]          # up, right, down, left\n"
         "    def __init__(self, room, r, c):\n"
         "        self.room, self.r, self.c, self.d, self.cleaned = room, r, c, 0, set()\n"
         "    def move(self):\n"
         "        nr, nc = self.r + self.STEP[self.d][0], self.c + self.STEP[self.d][1]\n"
         "        if 0 <= nr < len(self.room) and 0 <= nc < len(self.room[0]) and self.room[nr][nc]:\n"
         "            self.r, self.c = nr, nc\n"
         "            return True\n"
         "        return False\n"
         "    def turnRight(self):\n"
         "        self.d = (self.d + 1) % 4\n"
         "    def turnLeft(self):\n"
         "        self.d = (self.d - 1) % 4\n"
         "    def clean(self):\n"
         "        self.cleaned.add((self.r, self.c))\n"
         "room = [[1, 1, 0],\n"
         "        [1, 1, 1]]                       # 1 = open, 0 = wall\n"
         "robot = Robot(room, 1, 0)                # starts bottom-left, facing up\n"
         "clean_room(robot)")

WS_BOARD = 'board = [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]]'

EXPLAIN = {
    # ------------------------------------------------------------------ synonymous sentences
    "synonymous-sentences": {
        "example": {"call": 'generate_sentences([["happy", "joy"], ["joy", "cheerful"]], "I am happy")',
                    "expect": '["I am cheerful", "I am happy", "I am joy"]'},
        "approaches": {
            "Union-find groups, then backtrack word by word": {
                "idea": [
                    "Synonymy is transitive, so first merge the words into groups: happy~joy and joy~cheerful put all three together.",
                    "Then build sentences word by word: each position offers every word in its group (or just itself), so choose one, recurse, and un-choose.",
                    "Sorting each group once makes the sentences come out already in sorted order.",
                ],
                "steps": [
                    "Union every synonym pair; collect and sort each group.",
                    "<code>dfs(i)</code>: at the end of the sentence, record it; otherwise try each option for <code>words[i]</code>.",
                ],
                "why": [
                    "Union-find captures transitivity exactly, and the backtracking enumerates every combination once.",
                    "The work is proportional to the output: O(n + S·L) for S sentences of length L.",
                ],
                "dry": [
                    "The group {cheerful, happy, joy} is sorted as cheerful, happy, joy.",
                    "\"I\" and \"am\" have no synonyms, so one option each.",
                    "\"happy\" offers three options, giving \"I am cheerful\", \"I am happy\", \"I am joy\" in that order.",
                    "The result is <strong>[\"I am cheerful\", \"I am happy\", \"I am joy\"]</strong>.",
                ],
            },
            "BFS over whole sentences": {
                "idea": [
                    "Start from the original sentence and generate every sentence that differs by one direct synonym swap.",
                    "Keep a seen set and continue until nothing new appears; transitivity is handled by the repeated swaps.",
                ],
                "steps": [
                    "Build the synonym graph.",
                    "BFS: for each word position and each direct synonym, form the new sentence and enqueue it if unseen.",
                    "Return the sorted seen set.",
                ],
                "why": [
                    "It is correct, but each sentence is regenerated from every neighbour, and all sentences are stored in full.",
                ],
                "dry": [
                    "Start: \"I am happy\". Swapping happy for joy gives \"I am joy\".",
                    "From \"I am joy\": swapping joy for cheerful gives \"I am cheerful\"; back to happy is already seen.",
                    "Sorted: <strong>[\"I am cheerful\", \"I am happy\", \"I am joy\"]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subset xor totals
    "subset-xor-totals": {
        "example": {"call": "subset_xor_sum([5, 1, 6])", "expect": "28"},
        "approaches": {
            "Include / exclude recursion": {
                "idea": [
                    "Every element is either in a subset or not: a two-way branch at each index.",
                    "Carry the running XOR as an integer, so nothing is copied, and add it up at the leaves.",
                ],
                "steps": [
                    "<code>dfs(i, acc)</code>: at the end, return <code>acc</code>.",
                    "Otherwise return <code>dfs(i + 1, acc ^ nums[i]) + dfs(i + 1, acc)</code>.",
                ],
                "why": [
                    "Each of the 2<sup>n</sup> subsets is a distinct leaf: O(2<sup>n</sup>) time and O(n) depth.",
                ],
                "dry": [
                    "The XOR totals of the 8 subsets: {} 0, {5} 5, {1} 1, {6} 6.",
                    "{5, 1} 4, {5, 6} 3, {1, 6} 7, {5, 1, 6} 2.",
                    "Sum: 0 + 5 + 1 + 6 + 4 + 3 + 7 + 2 = <strong>28</strong>.",
                ],
            },
            "Bit contribution: OR &times; 2<sup>n-1</sup>": {
                "idea": [
                    "Look at one bit position. If some element has that bit, exactly half of all subsets have it set in their XOR (toggling that element pairs them up).",
                    "So each bit that appears anywhere contributes its value times 2<sup>n-1</sup>.",
                    "The total is therefore <code>(OR of all elements) &lt;&lt; (n - 1)</code>.",
                ],
                "steps": [
                    "OR everything together.",
                    "Shift it left by n - 1.",
                ],
                "why": [
                    "It is a counting argument per bit: O(n) time and O(1) space.",
                ],
                "dry": [
                    "5 | 1 | 6 = 101 | 001 | 110 = 111 = 7.",
                    "7 &lt;&lt; 2 = <strong>28</strong>, the same as the enumeration.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subsets
    "subsets": {
        "example": {"call": "sorted(subsets([1, 2, 3]))", "expect": "[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]"},
        "approaches": {
            "Backtracking with a start index": {
                "idea": [
                    "Every node of the recursion is a subset, not just the leaves: record the path on entry.",
                    "Then try adding each element <em>after</em> the last one used. Elements only ever join in increasing index order, so [1, 2] is built but [2, 1] never is.",
                ],
                "steps": [
                    "<code>dfs(start)</code>: record <code>path[:]</code>.",
                    "For i from start: append <code>nums[i]</code>, <code>dfs(i + 1)</code>, pop.",
                ],
                "why": [
                    "Each subset corresponds to exactly one increasing index sequence.",
                    "It is O(n·2<sup>n</sup>), the output size.",
                ],
                "dry": [
                    "Recorded in order: [], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3].",
                    "Sorted: <strong>[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]</strong>.",
                ],
            },
            "Iterative doubling": {
                "idea": [
                    "Start with just the empty subset. For each new element, every existing subset either takes it or not.",
                    "So append a copy of every existing subset with the element added; the list doubles each time.",
                ],
                "steps": [
                    "<code>out = [[]]</code>.",
                    "For each x: <code>out += [s + [x] for s in out]</code>.",
                ],
                "why": [
                    "After processing k elements, out holds exactly the 2<sup>k</sup> subsets of the first k.",
                ],
                "dry": [
                    "Start: [[]]. With 1: [], [1].",
                    "With 2: [], [1], [2], [1, 2].",
                    "With 3: the four above plus [3], [1, 3], [2, 3], [1, 2, 3].",
                    "Sorted, it matches: <strong>[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]</strong>.",
                ],
            },
            "Bitmasks": {
                "idea": [
                    "The integers 0 to 2<sup>n</sup> - 1 are exactly the subsets: bit i says whether <code>nums[i]</code> is included.",
                ],
                "steps": [
                    "For each mask, collect <code>nums[i]</code> where bit i is set.",
                ],
                "why": [
                    "There is no recursion, and a mask is a handy key when a later problem memoises on which elements are used.",
                ],
                "dry": [
                    "Masks 000, 001, 010, 011, 100, 101, 110, 111 give [], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3].",
                    "Sorted: <strong>[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ combination sum
    "combination-sum": {
        "example": {"call": "sorted(combination_sum([2, 3, 6, 7], 7))", "expect": "[[2, 2, 3], [7]]"},
        "approaches": {
            "Sorted candidates, recurse on the same index, break early": {
                "idea": [
                    "Build combinations in non-decreasing order, so each multiset is produced once.",
                    "Recursing with the <em>same</em> index i (not i + 1) allows a candidate to be reused.",
                    "With the candidates sorted, once one overshoots the remainder, every later one does too, so stop the loop.",
                ],
                "steps": [
                    "<code>dfs(start, remaining)</code>: record the path when remaining is 0.",
                    "For i from start: break if <code>candidates[i] &gt; remaining</code>; otherwise choose it, recurse with <code>(i, remaining - c)</code>, un-choose.",
                ],
                "why": [
                    "Never looking back at earlier candidates removes reorderings; the break prunes most of the tree.",
                    "Recursion depth is at most target / smallest candidate.",
                ],
                "dry": [
                    "[2] → [2, 2] → [2, 2, 2] leaves 1, and 2 &gt; 1, so break.",
                    "[2, 2, 3] leaves 0: record it. Back up: [2, 3] leaves 2, and 3 &gt; 2, so break.",
                    "[3] → [3, 3] leaves 1, a dead end. [6] leaves 1, a dead end.",
                    "[7] leaves 0: record it. The result is <strong>[[2, 2, 3], [7]]</strong>.",
                ],
            },
            "DP table of combinations per amount": {
                "idea": [
                    "This is the unbounded-knapsack loop, storing lists of combinations instead of counts.",
                    "Processing candidates in the outer loop keeps every combination non-decreasing, so there are no duplicates.",
                ],
                "steps": [
                    "<code>ways[0] = [[]]</code>.",
                    "For each candidate c, for amounts from c to target: <code>ways[a] += [combo + [c] for combo in ways[a - c]]</code>.",
                ],
                "why": [
                    "It stores every partial combination for every amount, far more memory than one backtracking path. It shows the connection to DP.",
                ],
                "dry": [
                    "c=2: ways[2] = [[2]], ways[4] = [[2, 2]], ways[6] = [[2, 2, 2]].",
                    "c=3: ways[3] = [[3]], ways[5] = [[2, 3]], ways[7] = [[2, 2, 3]].",
                    "c=6 adds nothing to 7. c=7: ways[7] gets [7].",
                    "ways[7] = <strong>[[2, 2, 3], [7]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ combination sum II
    "combination-sum-ii": {
        "example": {"call": "sorted(combination_sum2([10, 1, 2, 7, 6, 1, 5], 8))", "expect": "[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]"},
        "approaches": {
            "Sort, then skip equal siblings": {
                "idea": [
                    "Each element can be used once, so recurse with <code>i + 1</code>.",
                    "Duplicates in the input would produce the same combination twice. After sorting, skip a value at a given level if the same value was just tried at that level.",
                    "The condition <code>i &gt; start</code> limits the skip to siblings: the second 1 may still follow the first 1 one level deeper.",
                ],
                "steps": [
                    "Sort the candidates.",
                    "In the loop: skip if <code>i &gt; start</code> and <code>c[i] == c[i-1]</code>; break if <code>c[i] &gt; remaining</code>.",
                    "Choose, recurse with <code>(i + 1, remaining - c[i])</code>, un-choose.",
                ],
                "why": [
                    "Each distinct combination is generated from exactly one choice of positions.",
                ],
                "dry": [
                    "Sorted: [1, 1, 2, 5, 6, 7, 10].",
                    "First 1 → second 1 → 6 gives [1, 1, 6]. First 1 → 2 → 5 gives [1, 2, 5]. First 1 → 7 gives [1, 7].",
                    "The second 1 at the top level is a sibling of the first, so it is skipped and no combination is repeated.",
                    "2 → 6 gives [2, 6]. The result is <strong>[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ combinations
    "combinations": {
        "example": {"call": "combine(4, 2)", "expect": "[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]"},
        "approaches": {
            "Backtracking with an upper bound on the next choice": {
                "idea": [
                    "Choose numbers in increasing order. With <code>len(path)</code> numbers chosen, <code>k - len(path)</code> are still needed.",
                    "So the next choice can be at most <code>n - (k - len(path)) + 1</code>; anything larger leaves too few numbers to finish.",
                    "With that bound every branch completes, so the work matches the output.",
                ],
                "steps": [
                    "Record the path when it has length k.",
                    "Loop v from start to the bound: append, <code>dfs(v + 1)</code>, pop.",
                ],
                "why": [
                    "There are no dead branches: O(k·C(n, k)).",
                ],
                "dry": [
                    "Empty path: the bound is 4 - 2 + 1 = 3, so the first number is 1, 2 or 3 (4 is never tried first).",
                    "After 1: 2, 3, 4. After 2: 3, 4. After 3: 4.",
                    "The result is <strong>[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]</strong>.",
                ],
            },
            "itertools.combinations": {
                "idea": [
                    "The standard library generates combinations in the same lexicographic order, in C.",
                ],
                "steps": [
                    "<code>[list(c) for c in combinations(range(1, n + 1), k)]</code>.",
                ],
                "why": [
                    "Mention it, then write the backtracking yourself, because that is what is being tested.",
                ],
                "dry": [
                    "The pairs of 1..4 in order: <strong>[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ permutations
    "permutations": {
        "example": {"call": "sorted(permute([1, 2, 3]))", "expect": "[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]"},
        "approaches": {
            "Used flags": {
                "idea": [
                    "Fill positions one at a time; any element not yet used may go next.",
                    "A boolean array marks which elements are in use and is reset when backing out.",
                ],
                "steps": [
                    "At full length, record the path.",
                    "For each unused i: mark it, append, recurse, pop, unmark.",
                ],
                "why": [
                    "There are n! leaves of length n: O(n·n!), the output size. This version extends directly to Permutations II.",
                ],
                "dry": [
                    "1 first: then 2, 3 gives [1, 2, 3]; 3, 2 gives [1, 3, 2].",
                    "2 first: [2, 1, 3], [2, 3, 1]. 3 first: [3, 1, 2], [3, 2, 1].",
                    "That is 6 permutations: <strong>[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]</strong>.",
                ],
            },
            "Swap into place": {
                "idea": [
                    "Treat the array itself as the state: the prefix is the permutation built so far and the suffix is the unused pool.",
                    "Fill position i by swapping each suffix element into it, recurse on i + 1, and swap back.",
                ],
                "steps": [
                    "At i == n, record a copy.",
                    "For j from i: swap i and j, <code>dfs(i + 1)</code>, swap back.",
                ],
                "why": [
                    "It needs no flags and no path list: O(n·n!).",
                ],
                "dry": [
                    "i=0 keeps 1: [1, 2, 3], then [1, 3, 2].",
                    "Swap 2 in front: [2, 1, 3], [2, 3, 1]. Swap 3 in front: [3, 2, 1], [3, 1, 2].",
                    "Sorted: <strong>[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subsets II
    "subsets-ii": {
        "example": {"call": "sorted(subsets_with_dup([1, 2, 2]))", "expect": "[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]"},
        "approaches": {
            "Sort, skip equal siblings": {
                "idea": [
                    "This is the Subsets backtracking, plus the sibling-skip rule from Combination Sum II.",
                    "At one level, a value equal to its left neighbour was already tried as the next element, so skip it; one level deeper the duplicate may still follow its twin.",
                ],
                "steps": [
                    "Sort the array. Record the path on entry.",
                    "Skip if <code>i &gt; start</code> and <code>nums[i] == nums[i-1]</code>.",
                ],
                "why": [
                    "Each distinct subset is built exactly once: O(n·2<sup>n</sup>).",
                ],
                "dry": [
                    "Recorded: [], [1], [1, 2], [1, 2, 2].",
                    "Back at [1], the second 2 is a sibling, so it is skipped.",
                    "Top level: [2], [2, 2]; the second 2 at the top level is skipped.",
                    "Sorted: <strong>[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]</strong>.",
                ],
            },
            "Counts per distinct value": {
                "idea": [
                    "Group equal values: a value that occurs c times appears 0, 1, …, c times in a subset.",
                    "Extend every subset built so far with each possible count, so there are no duplicates to skip at all.",
                ],
                "steps": [
                    "For each (value, count) in sorted order: <code>out = [s + [value] * k for s in out for k in 0..count]</code>.",
                ],
                "why": [
                    "Every multiset is produced exactly once.",
                ],
                "dry": [
                    "Value 1 (count 1): [], [1].",
                    "Value 2 (count 2): [], [2], [2, 2], [1], [1, 2], [1, 2, 2].",
                    "Sorted: <strong>[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ permutations II
    "permutations-ii": {
        "example": {"call": "sorted(permute_unique([1, 1, 2]))", "expect": "[[1, 1, 2], [1, 2, 1], [2, 1, 1]]"},
        "approaches": {
            "Sort, skip a duplicate whose twin is unused": {
                "idea": [
                    "Equal values must be placed in their left-to-right order: the second 1 may only be used after the first 1 is already on the path.",
                    "That gives every distinct permutation exactly one way to be built.",
                    "The rule: skip i if <code>nums[i] == nums[i-1]</code> and <code>nums[i-1]</code> is not in use.",
                ],
                "steps": [
                    "Sort; use the flags as in Permutations, plus the skip rule.",
                ],
                "why": [
                    "Duplicates are prevented by construction; the worst case (all distinct) is the same as Permutations.",
                ],
                "dry": [
                    "First 1, then second 1, then 2: [1, 1, 2]. First 1, then 2, then second 1: [1, 2, 1].",
                    "Starting with the second 1 while the first is unused is skipped.",
                    "2, then first 1, then second 1: [2, 1, 1].",
                    "The result is <strong>[[1, 1, 2], [1, 2, 1], [2, 1, 1]]</strong>.",
                ],
            },
            "Choose from a Counter of remaining values": {
                "idea": [
                    "Loop over the <em>distinct</em> values that still have copies left, instead of over positions.",
                    "The same value is never tried twice at one depth, so duplicates cannot arise and no skip rule is needed.",
                ],
                "steps": [
                    "Decrement the count, append, recurse, pop, increment.",
                ],
                "why": [
                    "It is O(n·P) for P unique permutations.",
                ],
                "dry": [
                    "Counts {1: 2, 2: 1}.",
                    "1 → 1 → 2: [1, 1, 2]. 1 → 2 → 1: [1, 2, 1]. 2 → 1 → 1: [2, 1, 1].",
                    "The result is <strong>[[1, 1, 2], [1, 2, 1], [2, 1, 1]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ generate parentheses
    "generate-parentheses": {
        "example": {"call": "sorted(generate_parenthesis(3))", "expect": '["((()))", "(()())", "(())()", "()(())", "()()()"]'},
        "approaches": {
            "Add only what keeps the prefix valid": {
                "idea": [
                    "A prefix can still become valid exactly when it has used at most n opening brackets and never more closing than opening ones.",
                    "So add '(' while <code>open &lt; n</code>, and add ')' while <code>close &lt; open</code>.",
                    "Every branch then ends in a valid string, with no dead ends.",
                ],
                "steps": [
                    "<code>dfs(open, close)</code>: at length 2n, record the string.",
                    "Try '(' if allowed, then ')' if allowed.",
                ],
                "why": [
                    "The number of answers is the Catalan number C<sub>n</sub>, so the work is O(4<sup>n</sup>/√n).",
                ],
                "dry": [
                    "Always taking '(' first gives \"((()))\".",
                    "Backing up to \"((\" and closing early gives \"(()())\" and \"(())()\".",
                    "Starting with \"()\" gives \"()(())\" and \"()()()\".",
                    "Five strings: <strong>[\"((()))\", \"(()())\", \"(())()\", \"()(())\", \"()()()\"]</strong>.",
                ],
            },
            "Generate all 2<sup>2n</sup> strings, keep the valid ones": {
                "idea": [
                    "Generate every string of length 2n over '(' and ')' and keep those whose running balance never drops below 0 and ends at 0.",
                ],
                "steps": [
                    "<code>product(\"()\", repeat=2n)</code>, filtered by a balance check.",
                ],
                "why": [
                    "It does O(n·4<sup>n</sup>) work; the gap from the pruned version is exactly what pruning buys.",
                ],
                "dry": [
                    "For n = 3 there are 64 strings, and only 5 pass the balance check.",
                    "Sorted: <strong>[\"((()))\", \"(()())\", \"(())()\", \"()(())\", \"()()()\"]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word search
    "word-search": {
        "example": {"setup": 'board = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]',
                    "call": 'exist(board, "ABCCED")', "expect": "True"},
        "approaches": {
            "DFS with in-place marking and pruning": {
                "idea": [
                    "From each cell matching the next letter, step to an adjacent cell matching the letter after it, depth-first.",
                    "Mark a cell with '#' while it is on the current path so it cannot be reused, and restore it on the way back.",
                    "Cheap pruning first: if the board has too few copies of some letter, return <code>False</code> at once; and if the last letter is rarer than the first, search the reversed word (fewer starting cells).",
                ],
                "steps": [
                    "Check letter counts; reverse the word if that gives fewer starts.",
                    "<code>dfs(r, c, i)</code>: fail on a mismatch; succeed at the last letter; otherwise mark, try 4 neighbours, unmark.",
                ],
                "why": [
                    "Every path explored matches a prefix of the word.",
                    "It is O(R·C·3<sup>L</sup>) in the worst case, with O(L) recursion depth.",
                ],
                "dry": [
                    "A appears twice but D only once, so search for \"DECCBA\" instead.",
                    "The only D is at (2, 1); E is at (2, 2); C is at (1, 2); C is at (0, 2).",
                    "B is at (0, 1) and A at (0, 0): every letter matched.",
                    "The result is <strong>True</strong>, and the board is restored on the way out.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ palindrome partitioning
    "palindrome-partitioning": {
        "example": {"call": 'sorted(partition("aab"))', "expect": '[["a", "a", "b"], ["aa", "b"]]'},
        "approaches": {
            "Precomputed palindrome table + backtracking": {
                "idea": [
                    "Precompute <code>pal[i][j]</code>: is <code>s[i..j]</code> a palindrome? It fills from short to long: equal ends and a palindromic middle.",
                    "Then backtrack: from position i, try every end j whose piece is a palindrome, with an O(1) check, and continue from j + 1.",
                ],
                "steps": [
                    "Fill <code>pal</code> with i descending.",
                    "<code>dfs(i)</code>: at the end, record the path; otherwise for each j with <code>pal[i][j]</code>, choose <code>s[i:j+1]</code>.",
                ],
                "why": [
                    "The table costs O(n²) once; there can be up to 2<sup>n-1</sup> partitions to output.",
                ],
                "dry": [
                    "pal: \"a\", \"a\" and \"b\" are palindromes, \"aa\" is one, \"ab\" and \"aab\" are not.",
                    "From 0, take \"a\": from 1, take \"a\", then \"b\", giving [a, a, b]. \"ab\" fails.",
                    "From 0, take \"aa\", then \"b\", giving [aa, b]. \"aab\" fails.",
                    "The result is <strong>[[\"a\", \"a\", \"b\"], [\"aa\", \"b\"]]</strong>.",
                ],
            },
            "Check each piece by slicing": {
                "idea": [
                    "Same backtracking, but test each candidate piece on the spot with <code>piece == piece[::-1]</code>.",
                ],
                "steps": [
                    "For each end j, slice, compare with its reverse, and recurse if it is a palindrome.",
                ],
                "why": [
                    "It is simpler, but the same substrings are re-checked in many branches at O(n) each.",
                ],
                "dry": [
                    "The same two partitions are found, re-checking \"b\" in both branches.",
                    "The result is <strong>[[\"a\", \"a\", \"b\"], [\"aa\", \"b\"]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ restore IP addresses
    "restore-ip-addresses": {
        "example": {"call": 'sorted(restore_ip_addresses("25525511135"))', "expect": '["255.255.11.135", "255.255.111.35"]'},
        "approaches": {
            "Backtracking with length bounds": {
                "idea": [
                    "An address has exactly 4 parts of 1 to 3 digits, each 0..255, with no leading zeros.",
                    "Cut a part of length 1, 2 or 3 and recurse on the rest; stop if the remaining digits cannot fill the remaining parts (fewer than one each, or more than three each).",
                    "A leading zero or a value over 255 cannot be fixed by taking more digits, so <code>break</code>.",
                ],
                "steps": [
                    "<code>dfs(i)</code>: with 0 parts left, record if all digits are used.",
                    "Check the length bounds, then try sizes 1, 2, 3.",
                ],
                "why": [
                    "There are at most 3<sup>4</sup> = 81 cuts whatever the input: O(1).",
                ],
                "dry": [
                    "A first part of \"2\" leaves 10 digits for 3 parts, more than 9, so it is pruned. \"25\" leads only to dead ends.",
                    "\"255\" then \"255\" leaves \"11135\" for 2 parts.",
                    "\"1\" leaves 4 digits for 1 part, which is pruned. \"11\" leaves \"135\": valid. \"111\" leaves \"35\": valid.",
                    "The result is <strong>[\"255.255.11.135\", \"255.255.111.35\"]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ letter combinations
    "letter-combinations-phone": {
        "example": {"call": 'sorted(letter_combinations("23"))', "expect": '["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]'},
        "approaches": {
            "Backtracking one digit at a time": {
                "idea": [
                    "Position i chooses one letter from digit i's key; recurse to the next digit.",
                    "An empty input gives [], not [\"\"].",
                ],
                "steps": [
                    "<code>dfs(i)</code>: at the end, join and record.",
                    "For each letter of <code>KEYS[digits[i]]</code>: append, recurse, pop.",
                ],
                "why": [
                    "There are at most 4 letters per digit: O(n·4<sup>n</sup>).",
                ],
                "dry": [
                    "Digit 2 offers a, b, c; digit 3 offers d, e, f.",
                    "a: ad, ae, af. b: bd, be, bf. c: cd, ce, cf.",
                    "The result is <strong>[\"ad\", \"ae\", \"af\", \"bd\", \"be\", \"bf\", \"cd\", \"ce\", \"cf\"]</strong>.",
                ],
            },
            "itertools.product": {
                "idea": [
                    "The same Cartesian product, computed by the standard library.",
                ],
                "steps": [
                    "<code>product(*(KEYS[d] for d in digits))</code>, joined.",
                ],
                "why": [
                    "It has identical output and cost.",
                ],
                "dry": [
                    "product(\"abc\", \"def\") gives the 9 pairs: <strong>[\"ad\", \"ae\", \"af\", \"bd\", \"be\", \"bf\", \"cd\", \"ce\", \"cf\"]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ matchsticks to square
    "matchsticks-to-square": {
        "example": {"call": "makesquare([1, 1, 2, 2, 2])", "expect": "True"},
        "approaches": {
            "Fill four sides, longest sticks first": {
                "idea": [
                    "Reject early: the total must be divisible by 4, and no stick may be longer than a side.",
                    "Place sticks one at a time into any side with room. Longest first, so failures show up near the root of the search.",
                    "Two sides with the same current length are interchangeable, so try only one of them (the <code>tried</code> set).",
                ],
                "steps": [
                    "<code>side = total // 4</code>; sort the sticks in descending order.",
                    "<code>dfs(i)</code>: for each side with room and an untried length, add the stick, recurse, remove it.",
                ],
                "why": [
                    "When all sticks are placed without overflow, the four sides must be exactly equal.",
                    "It is exponential in the worst case, but pruning makes typical inputs fast.",
                ],
                "dry": [
                    "Total 8, so the side is 2. Sorted: [2, 2, 2, 1, 1].",
                    "2 goes on side 0. The next 2 does not fit there, so side 1. The next 2 goes on side 2.",
                    "1 goes on side 3, and the last 1 fills side 3.",
                    "All sides are 2: <strong>True</strong>.",
                ],
            },
            "Bitmask DP over used sticks": {
                "idea": [
                    "Fill the sides one after another. For a set of used sticks (a bitmask), the only thing that matters is how full the current side is: (sum used) mod side.",
                    "<code>fill[mask]</code> records that, or -1 if the set cannot be arranged with every completed side exact.",
                    "A stick can be added if it fits in the current side.",
                ],
                "steps": [
                    "<code>fill[0] = 0</code>.",
                    "For each reachable mask and each unused stick that fits, set the next mask's fill to <code>(fill + stick) % side</code>.",
                    "Answer: <code>fill[all] == 0</code>.",
                ],
                "why": [
                    "It is O(n·2<sup>n</sup>) regardless of input, safer on adversarial data, but with 2<sup>n</sup> memory.",
                ],
                "dry": [
                    "side = 2. Adding a 2-stick completes a side, so its fill wraps back to 0.",
                    "Two 1-sticks together also make 0.",
                    "The full mask is reached with fill 0, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ partition into k equal subsets
    "partition-k-equal-subsets": {
        "example": {"call": "can_partition_k_subsets([4, 3, 2, 3, 5, 2, 1], 4)", "expect": "True"},
        "approaches": {
            "Bucket filling with symmetry pruning": {
                "idea": [
                    "This is matchsticks with k buckets: the target is total / k, and numbers go in largest first.",
                    "Skip any bucket whose current sum has already been tried for this number; in particular, all empty buckets are identical, so a number tries only one of them.",
                ],
                "steps": [
                    "Reject if the total is not divisible by k or the largest number exceeds the target.",
                    "<code>dfs(i)</code>: try each bucket with room and an untried sum.",
                ],
                "why": [
                    "It is exponential in the worst case but fast in practice, because large numbers fail early.",
                ],
                "dry": [
                    "The target is 5. Sorted: [5, 4, 3, 3, 2, 2, 1].",
                    "5 goes to bucket 0, 4 to bucket 1, 3 to bucket 2, and the other 3 to bucket 3.",
                    "2 joins bucket 2 (3 + 2 = 5), the next 2 joins bucket 3 (5), and 1 joins bucket 1 (5).",
                    "All four buckets are 5: <strong>True</strong>.",
                ],
            },
            "Bitmask DP": {
                "idea": [
                    "The same DP as matchsticks, with target = total / k: for each set of used numbers, record how full the current bucket is.",
                ],
                "steps": [
                    "<code>fill[mask | bit] = (fill[mask] + nums[i]) % target</code> when it fits.",
                ],
                "why": [
                    "With n ≤ 16 that is 65,536 masks × 16 transitions, about a million steps, guaranteed.",
                ],
                "dry": [
                    "Buckets complete whenever the fill wraps to 0, for example 5, or 4 + 1, or 3 + 2.",
                    "The full mask is reachable with fill 0, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ factor combinations
    "factor-combinations": {
        "example": {"call": "sorted(get_factors(12))", "expect": "[[2, 2, 3], [2, 6], [3, 4]]"},
        "approaches": {
            "Factors in non-decreasing order, up to &radic;n": {
                "idea": [
                    "List factors in non-decreasing order so each combination appears once ([2, 6] but never [6, 2]).",
                    "For each divisor f ≥ start with f² ≤ n, the pair <code>path + [f, n/f]</code> is an answer, and n/f can be split further using factors ≥ f.",
                    "A factor above √n would need a smaller partner, which was already tried.",
                ],
                "steps": [
                    "<code>dfs(n, start)</code>: for f from start while <code>f·f &lt;= n</code>: if f divides n, record the pair, then recurse on <code>(n // f, f)</code>.",
                ],
                "why": [
                    "Depth is at most log<sub>2</sub> n; the work is about √n per level times the number of combinations.",
                ],
                "dry": [
                    "dfs(12, 2): f=2 divides, so record [2, 6], then split 6 with factors ≥ 2.",
                    "dfs(6, 2): f=2 divides, so record [2, 2, 3]; then dfs(3, 2) ends at once, since 2·2 &gt; 3.",
                    "Back in dfs(12, 2): f=3 divides, so record [3, 4]; dfs(4, 3) ends, since 9 &gt; 4. f=4: 16 &gt; 12, so stop.",
                    "The result is <strong>[[2, 2, 3], [2, 6], [3, 4]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ brace expansion
    "brace-expansion": {
        "example": {"call": 'expand("{a,b}c{d,e}f")', "expect": '["acdf", "acef", "bcdf", "bcef"]'},
        "approaches": {
            "Parse into option groups, backtrack in sorted order": {
                "idea": [
                    "Parse the string once into groups: a fixed letter is a group of one option, and <code>{…}</code> is a group of choices.",
                    "Sort each group, then pick one letter per group with backtracking.",
                    "All words have the same length, so picking in sorted order at every position emits them in sorted order.",
                ],
                "steps": [
                    "Parse into <code>groups</code>.",
                    "<code>dfs(g)</code>: for each option of group g, append it and recurse.",
                ],
                "why": [
                    "It is O(W·L) for W words of length L, the output size.",
                ],
                "dry": [
                    "Groups: [a, b], [c], [d, e], [f].",
                    "a, c, d, f gives \"acdf\"; a, c, e, f gives \"acef\".",
                    "b, c, d, f gives \"bcdf\"; b, c, e, f gives \"bcef\".",
                    "The result is <strong>[\"acdf\", \"acef\", \"bcdf\", \"bcef\"]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word pattern II
    "word-pattern-ii": {
        "example": {"call": 'word_pattern_match("abab", "redblueredblue")', "expect": "True"},
        "approaches": {
            "Backtrack over the length of each new mapping": {
                "idea": [
                    "Walk the pattern. An already-mapped letter leaves no choice: its string must appear next in s.",
                    "An unmapped letter tries every possible next substring, skipping strings already claimed by another letter (the mapping must be one-to-one).",
                    "Each remaining pattern letter needs at least one character, which caps how long the new string can be.",
                ],
                "steps": [
                    "<code>dfs(i, j)</code>: the pattern is used up exactly when s is.",
                    "Mapped letter: check <code>s.startswith(w, j)</code>. Unmapped letter: try each length, map, recurse, unmap.",
                ],
                "why": [
                    "Forced matches prune most branches.",
                    "It is exponential in the number of distinct letters at worst.",
                ],
                "dry": [
                    "a = \"r\": every choice of b then fails when a must reappear (for example b = \"e\" needs \"r\" at index 2, which is 'd').",
                    "a = \"re\" fails the same way.",
                    "a = \"red\": b = \"b\", \"bl\" and \"blu\" fail the forced check for the second a.",
                    "b = \"blue\": the forced checks for a = \"red\" and b = \"blue\" both pass, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ android unlock patterns
    "android-unlock-patterns": {
        "example": {"call": "number_of_patterns(1, 2)", "expect": "65"},
        "approaches": {
            "Backtracking with a skip table and symmetry": {
                "idea": [
                    "Precompute <code>skip[a][b]</code>, the key that the straight segment from a to b passes through (0 if none).",
                    "A move to b is legal when b is unvisited and its skip key is 0 or already visited.",
                    "Symmetry: the four corners behave alike, and so do the four edges. Count from 1, 2 and 5 and weight the counts by 4, 4 and 1.",
                ],
                "steps": [
                    "<code>dfs(cur, length)</code>: count this pattern if <code>length ≥ m</code>; stop at n; otherwise mark, try all legal next keys, unmark.",
                    "Return <code>4·dfs(1) + 4·dfs(2) + dfs(5)</code>.",
                ],
                "why": [
                    "The search tree has at most 9! leaves, a constant; symmetry cuts the work to a third.",
                ],
                "dry": [
                    "From 1: the 1-key pattern counts 1; legal second keys are 2, 4, 5, 6, 8 (3, 7 and 9 need an unvisited middle). Total 6.",
                    "From 2: 1, plus 7 legal second keys (only 8 is blocked by 5). Total 8.",
                    "From 5: 1, plus all 8 others. Total 9.",
                    "4·6 + 4·8 + 9 = <strong>65</strong>.",
                ],
            },
            "Backtracking from all nine keys": {
                "idea": [
                    "Run the same search from every starting key, without the symmetry argument.",
                ],
                "steps": [
                    "Return <code>sum(dfs(k, 1) for k in 1..9)</code>.",
                ],
                "why": [
                    "It does three times the work, and is a useful check that the symmetry weighting is right.",
                ],
                "dry": [
                    "Corners give 6 each (24), edges 8 each (32), the centre 9.",
                    "The total is <strong>65</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ N-Queens
    "n-queens": {
        "example": {"call": "sorted(solve_n_queens(4))", "expect": '[["..Q.", "Q...", "...Q", ".Q.."], [".Q..", "...Q", "Q...", "..Q."]]'},
        "approaches": {
            "One row at a time, three sets of attacked lines": {
                "idea": [
                    "Place one queen per row, choosing its column.",
                    "A queen attacks its column and two diagonals. Along one diagonal <code>r - c</code> is constant, and along the other <code>r + c</code> is.",
                    "Three sets of attacked columns and diagonals make each safety check O(1).",
                ],
                "steps": [
                    "<code>dfs(r)</code>: at r == n, build the board strings.",
                    "For each safe column: add it to the three sets, recurse, remove it.",
                ],
                "why": [
                    "Row r has at most n - r safe columns, so there are at most n! leaves; attacks prune far below that.",
                ],
                "dry": [
                    "Row 0, column 0: every continuation dies by row 2 or row 3.",
                    "Row 0, column 1 → row 1, column 3 → row 2, column 0 → row 3, column 2: a solution.",
                    "Row 0, column 2 gives the mirror image: columns 2, 0, 3, 1. Row 0, column 3 fails.",
                    "Sorted (a '.' sorts before 'Q'): <strong>[[\"..Q.\", \"Q...\", \"...Q\", \".Q..\"], [\".Q..\", \"...Q\", \"Q...\", \"..Q.\"]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ N-Queens II
    "n-queens-ii": {
        "example": {"call": "total_n_queens(4)", "expect": "2"},
        "approaches": {
            "Bitmask backtracking": {
                "idea": [
                    "Track occupied columns and the squares attacked by each family of diagonals on the current row as n-bit integers.",
                    "The free squares are <code>~(cols | d1 | d2) &amp; full</code>; take the lowest free bit with <code>free &amp; -free</code>.",
                    "Moving down a row, the diagonal masks shift by one bit, left for one family and right for the other.",
                ],
                "steps": [
                    "<code>dfs(cols, d1, d2)</code>: count 1 when every column is used.",
                    "For each free bit: recurse with the shifted masks.",
                ],
                "why": [
                    "It is the same search tree as the set version, with every operation a few bit instructions.",
                ],
                "dry": [
                    "Row 0 tries column 0: the masks leave only dead ends.",
                    "Column 1 leads to the queens at columns 1, 3, 0, 2: count 1.",
                    "Column 2 gives the mirror image: count 1. Column 3 fails.",
                    "The total is <strong>2</strong>.",
                ],
            },
            "Sets of attacked lines": {
                "idea": [
                    "The N-Queens search, returning a count instead of boards.",
                ],
                "steps": [
                    "Same three sets; return 1 at r == n and add up the results.",
                ],
                "why": [
                    "It explores the same tree, with a slower constant than the bitmasks.",
                ],
                "dry": [
                    "The search finds the two placements (1, 3, 0, 2) and (2, 0, 3, 1).",
                    "The result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word break II
    "word-break-ii": {
        "example": {"call": 'sorted(word_break("catsanddog", ["cat", "cats", "and", "sand", "dog"]))', "expect": '["cat sand dog", "cats and dog"]'},
        "approaches": {
            "Memoised sentences per suffix": {
                "idea": [
                    "<code>sentences(i)</code> returns every way to split <code>s[i:]</code>; it depends only on i, so cache it.",
                    "A suffix that cannot be split is computed once and returns []; every later branch reaching it gets that instantly.",
                ],
                "steps": [
                    "<code>sentences(len(s)) = [\"\"]</code>.",
                    "For each dictionary word <code>s[i:j]</code>, prefix it to every sentence of <code>sentences(j)</code>.",
                ],
                "why": [
                    "It is O(n²) substring checks plus the output, which can be exponential and cannot be avoided.",
                ],
                "dry": [
                    "sentences(7) gives [\"dog\"].",
                    "sentences(3) (\"sanddog\"): \"sand\" + \"dog\". sentences(4) (\"anddog\"): \"and\" + \"dog\".",
                    "sentences(0): \"cat\" + \"sand dog\", and \"cats\" + \"and dog\".",
                    "The result is <strong>[\"cat sand dog\", \"cats and dog\"]</strong>.",
                ],
            },
            "Backtracking pruned by a word-break table": {
                "idea": [
                    "First compute <code>ok[i]</code>: can <code>s[i:]</code> be split at all? This is Word Break I, run backwards.",
                    "Then backtrack normally, but only step to positions where <code>ok</code> is <code>True</code>, so every branch leads to at least one sentence.",
                ],
                "steps": [
                    "Fill <code>ok</code> from the right.",
                    "<code>dfs(i)</code>: for each j with <code>ok[j]</code> and <code>s[i:j]</code> a word, choose it and recurse.",
                ],
                "why": [
                    "It uses less memory than caching sentence lists, but rebuilds shared suffixes for each prefix that reaches them.",
                ],
                "dry": [
                    "ok is True at 0, 3, 4, 7 and 10.",
                    "From 0: \"cat\" → 3, \"sand\" → 7, \"dog\" → 10, giving \"cat sand dog\".",
                    "From 0: \"cats\" → 4, \"and\" → 7, \"dog\" → 10, giving \"cats and dog\".",
                    "The result is <strong>[\"cat sand dog\", \"cats and dog\"]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ robot room cleaner
    "robot-room-cleaner": {
        "example": {"setup": ROBOT, "call": "sorted(robot.cleaned)", "expect": "[(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)]"},
        "approaches": {
            "DFS in the robot's own coordinates, physically backtracking": {
                "idea": [
                    "The real position is hidden, so invent coordinates: call the start (0, 0) and the initial heading \"up\". Every successful move updates this private position, so a visited set works as in any grid DFS.",
                    "From each cell, try the four directions clockwise, turning right after each attempt; four right turns restore the original heading.",
                    "After exploring a neighbour, the robot must physically walk back: turn around, move, turn around again. That is the un-choose step.",
                ],
                "steps": [
                    "<code>dfs(cell, d)</code>: mark it visited and clean it.",
                    "For k in 0..3: if the next cell is unvisited and <code>move()</code> succeeds, recurse, then <code>go_back()</code>. Then <code>turnRight()</code>.",
                ],
                "why": [
                    "Each open cell is entered once and each move is undone once: O(N) moves, O(N) space.",
                ],
                "dry": [
                    "Clean the start (bottom-left). Up is open: move and clean the top-left.",
                    "From there, up is a wall; turn right; right is open: clean the top-middle.",
                    "Right is a wall, so turn to face down: clean the bottom-middle. Left is already visited; up is visited; right is open: clean the bottom-right.",
                    "Every neighbour of the bottom-right is blocked or visited, so the robot walks back cell by cell to the start.",
                    "Cleaned: <strong>[(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)]</strong>, every open cell.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word search II
    "word-search-ii": {
        "example": {"setup": WS_BOARD, "call": 'sorted(find_words([row[:] for row in board], ["oath", "pea", "eat", "rain"]))',
                    "expect": '["eat", "oath"]'},
        "approaches": {
            "Trie-guided DFS, pruning found words": {
                "idea": [
                    "Put all the words in a trie; a node stores the whole word that ends there.",
                    "Start a DFS only from cells whose letter begins some word, and only step to neighbours whose letter is a child of the current trie node. Every path explored is the prefix of a real word.",
                    "Remove a word from the trie once found so it is reported once, and drop trie branches that become empty on the way back.",
                ],
                "steps": [
                    "Build the trie, storing <code>\"$\": word</code> at each word end.",
                    "<code>dfs(r, c, parent)</code>: move to the child node; if it ends a word, pop it into <code>out</code>; mark the cell, recurse into matching neighbours, unmark; prune an empty child.",
                ],
                "why": [
                    "The search is shared across all words, instead of repeated once per word.",
                    "It is O(R·C·3<sup>L</sup>) worst case, paid once.",
                ],
                "dry": [
                    "The trie holds oath, pea, eat and rain. Only cells with o, p, e or r start a search.",
                    "From 'o' at (0, 0): a (0, 1) → t (1, 1) → h (2, 1) completes \"oath\".",
                    "From 'e' at (1, 3): a (1, 2) → t (1, 1) completes \"eat\".",
                    "\"pea\" has no p on the board, and \"rain\" fails after r, a.",
                    "Sorted: <strong>[\"eat\", \"oath\"]</strong>.",
                ],
            },
            "Word Search once per word": {
                "idea": [
                    "Run the single-word search separately for each word.",
                ],
                "steps": [
                    "Keep each distinct word for which <code>exist(word)</code> succeeds.",
                ],
                "why": [
                    "It is fine for a handful of words; with thousands sharing prefixes, it repeats the work the trie shares.",
                ],
                "dry": [
                    "\"oath\" is found, \"pea\" is not, \"eat\" is found, \"rain\" is not.",
                    "Sorted: <strong>[\"eat\", \"oath\"]</strong>.",
                ],
            },
        },
    },
}
