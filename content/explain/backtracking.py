"""Write-ups for the Backtracking topic."""

ROBOT_CLASS = ("class Robot:\n"
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
               "        self.cleaned.add((self.r, self.c))\n")

ROBOT_1 = (ROBOT_CLASS +
           "room = [[1, 1, 0],\n"
           "        [1, 1, 1]]                       # 1 = open, 0 = wall\n"
           "robot = Robot(room, 1, 0)                # starts bottom-left, facing up\n"
           "clean_room(robot)")

ROBOT_2 = (ROBOT_CLASS +
           "room = [[1, 1, 1]]                       # a one-row corridor\n"
           "robot = Robot(room, 0, 1)                # starts in the middle, facing up\n"
           "clean_room(robot)")

WS_BOARD = 'board = [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]]'

WORD_BOARD = 'board = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]'

EXPLAIN = {
    # ------------------------------------------------------------------ synonymous sentences
    "synonymous-sentences": {
        "examples": [
            {"call": 'generate_sentences([["happy", "joy"], ["joy", "cheerful"]], "I am happy")',
             "expect": '["I am cheerful", "I am happy", "I am joy"]'},
            {"call": 'generate_sentences([["sad", "blue"]], "sad and sad")',
             "expect": '["blue and blue", "blue and sad", "sad and blue", "sad and sad"]'},
        ],
        "approaches": {
            "Union-find groups, then backtrack word by word": {
                "idea": [
                    "Synonymy is transitive: happy~joy and joy~cheerful make happy and cheerful synonyms too, even though no pair says so. Union-find merges words into exactly these groups.",
                    "Once every word knows its group, a sentence is built position by position: each word offers every member of its group (or just itself), so choose one, recurse on the next position, then un-choose.",
                    "Sorting each group once means the depth-first order already produces the sentences in sorted order, with no final sort.",
                ],
                "steps": [
                    "For each pair <code>(a, b)</code>, link the roots: <code>parent[find(a)] = find(b)</code>. <code>find</code> creates a word on first sight and halves the path as it climbs.",
                    "Collect every word in <code>parent</code> under its root in <code>groups</code>, then sort each group.",
                    "Split the text into <code>words</code>. <code>dfs(i)</code> handles position <code>i</code>, with the chosen words so far in <code>path</code>.",
                    "If <code>i == len(words)</code>, join <code>path</code> with spaces and append it to <code>out</code>.",
                    "Otherwise the options are <code>groups[find(w)]</code> when <code>w</code> has synonyms, else just <code>[w]</code>. For each option: append it, call <code>dfs(i + 1)</code>, pop it.",
                ],
                "why": [
                    "Two words share a root exactly when a chain of synonym pairs connects them, so each group is the full set of words interchangeable with any member.",
                    "Positions are independent, so the sentences are the Cartesian product of the option lists. The recursion visits each combination once, so nothing is repeated or missed.",
                    "Building the groups is near-linear in the number of pairs n. Each of the S sentences costs O(L) to join, so time is <strong>O(n + S · L)</strong>.",
                    "Space is <strong>O(n + L)</strong> beyond the output: the union-find and groups hold the n synonym words, and <code>path</code> plus the recursion hold at most L words.",
                ],
                "dry": [
                    [
                        "Pair (happy, joy): parent[happy] = joy. Pair (joy, cheerful): parent[joy] = cheerful.",
                        "Grouping: find(happy) climbs happy → joy → cheerful, so all three land under root cheerful. Sorted group: [cheerful, happy, joy].",
                        "words = [I, am, happy]. \"I\" and \"am\" are not in <code>parent</code>, so each offers only itself.",
                        "At i=2, \"happy\" offers cheerful, happy, joy in turn; each reaches i=3 and is recorded.",
                        "The result is <strong>[\"I am cheerful\", \"I am happy\", \"I am joy\"]</strong>, already sorted.",
                    ],
                    [
                        "Pair (sad, blue): parent[sad] = blue. The only group is [blue, sad] after sorting.",
                        "words = [sad, and, sad]. Position 0 offers [blue, sad], position 1 offers [and], position 2 offers [blue, sad].",
                        "Choosing blue at 0: position 2 gives \"blue and blue\", then \"blue and sad\".",
                        "Choosing sad at 0: position 2 gives \"sad and blue\", then \"sad and sad\".",
                        "The two occurrences of \"sad\" vary independently: <strong>[\"blue and blue\", \"blue and sad\", \"sad and blue\", \"sad and sad\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just swap each word for its direct synonyms?",
                     "Direct pairs miss transitive links. With pairs happy~joy and joy~cheerful, \"happy\" has no direct pair with \"cheerful\", but the answer must still contain \"I am cheerful\"."],
                    ["Why check <code>w in parent</code> before calling <code>find(w)</code>?",
                     "<code>find</code> uses <code>setdefault</code>, so calling it on a plain word like \"I\" would add it to <code>parent</code>. The check keeps ordinary words as single fixed options without touching the structure."],
                    ["Why is the output sorted without calling <code>sorted</code>?",
                     "The recursion fixes words left to right and tries each group's options in sorted order, so sentences come out ordered by first word, then second, and so on, which is how string comparison orders them here."],
                ],
            },
            "BFS over whole sentences": {
                "idea": [
                    "Treat each full sentence as a node. Two sentences are neighbours when they differ in one word that was swapped for a <em>direct</em> synonym.",
                    "Every reachable sentence is a valid answer, because chains of direct swaps cover the transitive groups automatically.",
                    "A breadth-first search from the original text with a <code>seen</code> set finds them all; sort at the end.",
                ],
                "steps": [
                    "Build <code>graph</code>, an undirected adjacency set: for each pair add <code>b</code> to <code>graph[a]</code> and <code>a</code> to <code>graph[b]</code>.",
                    "Start with <code>seen = {text}</code> and a <code>queue</code> holding <code>text</code>.",
                    "Pop a sentence and split it into <code>words</code>.",
                    "For every position <code>i</code> and every direct synonym <code>alt</code> of <code>words[i]</code>, rebuild the sentence <code>nxt</code> with that one word replaced.",
                    "If <code>nxt</code> is new, add it to <code>seen</code> and the queue. When the queue empties, return <code>sorted(seen)</code>.",
                ],
                "why": [
                    "Any valid sentence can be reached from the original by changing one word at a time along synonym chains, so BFS reaches all of them; it never leaves the valid set because each swap uses a real synonym.",
                    "The <code>seen</code> set makes each sentence enter the queue once, so the search terminates.",
                    "Each of the S sentences is split and, for each of its L positions, every direct synonym produces a new O(L) string, giving about <strong>O(S · L · P)</strong> time where P bounds the synonyms per word, plus the final sort.",
                    "All S sentences are stored whole in <code>seen</code> and the queue: <strong>O(S · L)</strong> space. The backtracking version stores only one partial sentence.",
                ],
                "dry": [
                    [
                        "graph: happy–joy, joy–cheerful. seen = {\"I am happy\"}.",
                        "Pop \"I am happy\": \"I\" and \"am\" have no synonyms; \"happy\" → joy gives \"I am joy\", which is new.",
                        "Pop \"I am joy\": joy's neighbours are happy (already seen) and cheerful, giving the new \"I am cheerful\".",
                        "Pop \"I am cheerful\": cheerful → joy gives \"I am joy\", already seen. The queue is empty.",
                        "sorted(seen) is <strong>[\"I am cheerful\", \"I am happy\", \"I am joy\"]</strong>.",
                    ],
                    [
                        "graph: sad–blue. Start with \"sad and sad\".",
                        "Pop it: position 0 gives \"blue and sad\", position 2 gives \"sad and blue\". Both are new.",
                        "Pop \"blue and sad\": position 0 swaps back to a seen sentence; position 2 gives the new \"blue and blue\".",
                        "Pop \"sad and blue\" and then \"blue and blue\": every swap leads to a seen sentence.",
                        "Four sentences were seen; sorted: <strong>[\"blue and blue\", \"blue and sad\", \"sad and blue\", \"sad and sad\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Does BFS handle transitive synonyms without union-find?",
                     "Yes. happy → joy → cheerful takes two swaps, and BFS keeps expanding until nothing new appears, so the chain is followed to the end."],
                    ["Why is it slower than the union-find version?",
                     "Each sentence is generated once per neighbour that leads to it, and every generation rebuilds a full string. The backtracking version produces each sentence exactly once, word by word."],
                    ["Why is the final <code>sorted</code> needed here?",
                     "BFS discovers sentences in order of how many swaps they need, not alphabetically, and a set has no order at all."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subset xor totals
    "subset-xor-totals": {
        "examples": [
            {"call": "subset_xor_sum([5, 1, 6])", "expect": "28"},
            {"call": "subset_xor_sum([1, 3])", "expect": "6"},
        ],
        "approaches": {
            "Include / exclude recursion": {
                "idea": [
                    "Every subset is a sequence of yes/no decisions, one per element. A recursion that makes those decisions in order reaches each subset exactly once, at a leaf.",
                    "Carry the XOR of the chosen elements down as <code>acc</code>, so a leaf already knows its subset's XOR total.",
                    "Each call returns the sum of the totals in its subtree, so the root returns the answer.",
                ],
                "steps": [
                    "<code>dfs(i, acc)</code> has decided elements 0..i−1, and <code>acc</code> is the XOR of those taken.",
                    "If <code>i == len(nums)</code>, the subset is complete: return <code>acc</code>.",
                    "Otherwise branch twice: take it with <code>dfs(i + 1, acc ^ nums[i])</code>, skip it with <code>dfs(i + 1, acc)</code>.",
                    "Return the sum of the two branches.",
                    "Start with <code>dfs(0, 0)</code>: nothing decided yet, the empty XOR is 0.",
                ],
                "why": [
                    "The take/skip choices form a binary tree whose 2<sup>n</sup> leaves are exactly the 2<sup>n</sup> subsets, so every subset contributes its XOR once.",
                    "The empty subset is the leaf that skipped everything; it returns 0, which matches the definition.",
                    "There are about 2<sup>n+1</sup> calls with O(1) work each: <strong>O(2<sup>n</sup>)</strong> time.",
                    "Only the current root-to-leaf chain is on the call stack: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Take 5 (acc 5): take 1 (acc 4) gives leaves 4^6 = 2 and 4; skip 1 (acc 5) gives 5^6 = 3 and 5. Subtree sum 2 + 4 + 3 + 5 = 14.",
                        "Skip 5 (acc 0): take 1 (acc 1) gives 1^6 = 7 and 1; skip 1 gives 6 and 0. Subtree sum 7 + 1 + 6 + 0 = 14.",
                        "All 8 leaves were visited, one per subset.",
                        "The root returns 14 + 14 = <strong>28</strong>.",
                    ],
                    [
                        "dfs(0, 0) first takes 1: dfs(1, 1).",
                        "dfs(1, 1): take 3 gives leaf 1^3 = 2, skip gives leaf 1. Sum 3.",
                        "Back at the root, skip 1: dfs(1, 0). Take 3 gives leaf 3, skip gives leaf 0. Sum 3.",
                        "The subsets {1,3}, {1}, {3}, {} give 2 + 1 + 3 + 0 = <strong>6</strong>.",
                    ],
                ],
                "faq": [
                    ["Why pass <code>acc</code> down instead of building a list of chosen elements?",
                     "Only the XOR matters, and XOR can be updated in O(1) per choice. Keeping a list and XOR-ing it at each leaf would add an O(n) factor."],
                    ["Is there an un-choose step here?",
                     "Not explicitly: <code>acc</code> is passed by value, so the skip branch simply uses the old <code>acc</code>. That is backtracking with immutable state."],
                    ["How large can n be before this is too slow?",
                     "2<sup>n</sup> leaves means about a million calls at n = 20 and a billion at n = 30. The problem's limit is small, which is why the recursion is accepted; the bit trick removes the limit."],
                ],
            },
            "Bit contribution: OR &times; 2<sup>n-1</sup>": {
                "idea": [
                    "Look at one bit position at a time. A subset's XOR has that bit set exactly when the subset contains an odd number of elements with the bit set.",
                    "If at least one element has the bit, exactly half of the 2<sup>n</sup> subsets contain an odd number of them. Toggling that one element pairs every subset with a partner of opposite parity.",
                    "So every bit that appears anywhere (the OR of all elements) is set in 2<sup>n−1</sup> subset totals, and the answer is <code>OR · 2<sup>n−1</sup></code>.",
                ],
                "steps": [
                    "Compute the OR of all numbers with <code>reduce(or_, nums, 0)</code>.",
                    "Shift it left by <code>len(nums) - 1</code>, which multiplies it by 2<sup>n−1</sup>.",
                    "Return the result.",
                    "A bit missing from every element is missing from the OR, so it correctly contributes nothing.",
                ],
                "why": [
                    "Fix an element x with bit b set. Adding or removing x flips the parity of bit b, and it pairs the subsets into 2<sup>n−1</sup> pairs with one odd, one even.",
                    "Bit b therefore adds 2<sup>b</sup> to the totals of exactly 2<sup>n−1</sup> subsets. Summing over the bits in the OR gives OR · 2<sup>n−1</sup>.",
                    "One pass to OR the numbers and one shift: <strong>O(n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "OR: 5 | 1 = 5 (101), then 5 | 6 = 7 (111).",
                        "n = 3, so shift left by 2, multiplying by 4.",
                        "Each of the three bits is set in 4 of the 8 subset totals.",
                        "7 · 4 = <strong>28</strong>.",
                    ],
                    [
                        "OR: 1 | 3 = 3 (11).",
                        "n = 2, so shift left by 1, multiplying by 2.",
                        "Check: totals 0, 1, 3, 2 have bit 0 set twice and bit 1 set twice.",
                        "3 · 2 = <strong>6</strong>.",
                    ],
                ],
                "faq": [
                    ["Why OR and not XOR of all elements?",
                     "The XOR of all elements is one subset's total. What matters is whether a bit appears in <em>any</em> element, because one such element is enough to split the subsets evenly; that is exactly OR."],
                    ["What if the list is empty?",
                     "Then <code>len(nums) - 1</code> is −1 and a negative shift raises ValueError. The problem guarantees at least one element; the recursion would return 0 for an empty list."],
                    ["Should I lead with this in an interview?",
                     "Give the recursion first, since the problem is listed under backtracking, then derive the parity argument. The argument is the part that impresses, not the one-liner."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subsets
    "subsets": {
        "examples": [
            {"call": "sorted(subsets([1, 2, 3]))",
             "expect": "[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]"},
            {"call": "subsets([])", "expect": "[[]]"},
        ],
        "approaches": {
            "Backtracking with a start index": {
                "idea": [
                    "Build subsets in increasing index order: once element <code>i</code> is in <code>path</code>, only elements after it may be added. That alone prevents both [1, 2] and [2, 1].",
                    "Every node of this recursion tree, not just the leaves, is a different subset, so record <code>path</code> on entry to every call.",
                    "Choose, explore, un-choose: append <code>nums[i]</code>, recurse from <code>i + 1</code>, pop it.",
                ],
                "steps": [
                    "Keep <code>out</code> for the answers and <code>path</code> for the subset being built.",
                    "<code>dfs(start)</code> first appends a copy <code>path[:]</code> to <code>out</code>.",
                    "Then for each <code>i</code> from <code>start</code> to the end: append <code>nums[i]</code> to <code>path</code>.",
                    "Recurse with <code>dfs(i + 1)</code>, so later choices come strictly after <code>i</code>.",
                    "Pop <code>nums[i]</code> to restore <code>path</code> before trying the next <code>i</code>. Call <code>dfs(0)</code> and return <code>out</code>.",
                ],
                "why": [
                    "Each subset, listed in index order, corresponds to exactly one path from the root: pick its smallest index first, then the next, and so on. So each subset is recorded exactly once.",
                    "Copying with <code>path[:]</code> matters: <code>path</code> keeps changing, and storing the list itself would leave every entry pointing at the same, finally empty, list.",
                    "There are 2<sup>n</sup> nodes and each copy costs up to n: <strong>O(n · 2<sup>n</sup>)</strong> time.",
                    "The recursion depth and <code>path</code> are at most n: <strong>O(n)</strong> extra space beyond the output.",
                ],
                "dry": [
                    [
                        "dfs(0) records []. i=0: path [1], dfs(1) records [1].",
                        "dfs(1): i=1 gives [1, 2], whose dfs(2) records it and then [1, 2, 3]. i=2 gives [1, 3].",
                        "Back at dfs(0): i=1 gives [2], then [2, 3]. i=2 gives [3].",
                        "Recorded in order: [], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3], which is already sorted.",
                        "The result is <strong>[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]</strong>.",
                    ],
                    [
                        "nums is empty. dfs(0) records a copy of the empty path.",
                        "The loop <code>range(0, 0)</code> is empty, so there is nothing else to try.",
                        "The empty set is still a subset of the empty set.",
                        "The result is <strong>[[]]</strong>, not [].",
                    ],
                ],
                "faq": [
                    ["Why record at every node instead of only when <code>start == len(nums)</code>?",
                     "Here a path ends wherever you stop adding. Recording only at the end would give just the subsets that include the last element."],
                    ["Why <code>dfs(i + 1)</code> and not <code>dfs(start + 1)</code>?",
                     "The next element must come after the one just chosen. With <code>start + 1</code>, choosing index 2 at start 0 would allow index 1 next, producing [3, 2] as well as [2, 3]."],
                    ["What does <code>path[:]</code> protect against?",
                     "Without the copy every recorded entry is the same list object, and after the final pops they would all be []."],
                ],
            },
            "Iterative doubling": {
                "idea": [
                    "The subsets of the first k elements, plus a new element x, give the subsets of k + 1 elements: every old subset, and every old subset with x added.",
                    "So start with just the empty subset and double the list once per element.",
                    "No recursion and no un-choose step: each new subset is a fresh list <code>s + [x]</code>.",
                ],
                "steps": [
                    "Start with <code>out = [[]]</code>.",
                    "For each <code>x</code> in <code>nums</code>, build <code>[s + [x] for s in out]</code>.",
                    "The comprehension is fully built before <code>+=</code> extends <code>out</code>, so it only sees the old subsets.",
                    "After the last element, <code>out</code> holds all 2<sup>n</sup> subsets. Return it.",
                ],
                "why": [
                    "Every subset of the first k + 1 elements either lacks x (already in <code>out</code>) or contains it (an old subset plus x), and these two groups do not overlap.",
                    "The list doubles n times, ending with 2<sup>n</sup> subsets.",
                    "Creating each new list costs its length, up to n: <strong>O(n · 2<sup>n</sup>)</strong> time.",
                    "Apart from the output, only the comprehension's temporary list is used: <strong>O(1)</strong> extra beyond the output (the temporary list is itself at most half the output).",
                ],
                "dry": [
                    [
                        "Start: [[]].",
                        "x=1: add [1]. out = [[], [1]].",
                        "x=2: add [2], [1, 2]. out = [[], [1], [2], [1, 2]].",
                        "x=3: add [3], [1, 3], [2, 3], [1, 2, 3].",
                        "Sorted, that is <strong>[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]</strong>.",
                    ],
                    [
                        "Start: [[]].",
                        "The loop over <code>nums</code> runs zero times.",
                        "Nothing is doubled; the starting list is the answer.",
                        "The result is <strong>[[]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>out += [s + [x] for s in out]</code> not loop forever?",
                     "The right-hand side is a complete new list before the extension begins, so it iterates over the old <code>out</code> only."],
                    ["Could I write <code>for s in out: out.append(s + [x])</code>?",
                     "No: that loop sees the items it just appended and never ends. Build the new batch first, or iterate over a copy."],
                    ["How does the output order differ from the backtracking version?",
                     "Doubling groups subsets by their largest element ([], [1], [2], [1, 2], ...); backtracking lists them in depth-first order ([], [1], [1, 2], ...). Both contain the same subsets."],
                ],
            },
            "Bitmasks": {
                "idea": [
                    "A subset of n elements is n yes/no answers, which is exactly an n-bit number. Bit i of <code>mask</code> says whether <code>nums[i]</code> is in.",
                    "The numbers 0 to 2<sup>n</sup> − 1 run through every possible bit pattern once, so they list every subset once.",
                ],
                "steps": [
                    "Let <code>n = len(nums)</code>.",
                    "Loop <code>mask</code> over <code>range(1 &lt;&lt; n)</code>, that is 0 to 2<sup>n</sup> − 1.",
                    "For each mask, keep <code>nums[i]</code> for every <code>i</code> where <code>mask &gt;&gt; i &amp; 1</code> is 1.",
                    "Collect these lists and return them.",
                ],
                "why": [
                    "The map from mask to subset is a bijection: different masks differ in some bit, so their subsets differ in that element.",
                    "2<sup>n</sup> masks, each checked against n bits: <strong>O(n · 2<sup>n</sup>)</strong> time.",
                    "Nothing is kept besides the output and the loop counters: <strong>O(1)</strong> extra beyond the output.",
                    "It only works while n is small enough for 2<sup>n</sup> to be enumerated, which is true for any problem asking for all subsets.",
                ],
                "dry": [
                    [
                        "n = 3, masks 0..7.",
                        "0 → [], 1 → [1], 2 → [2], 3 → [1, 2].",
                        "4 → [3], 5 → [1, 3], 6 → [2, 3], 7 → [1, 2, 3].",
                        "Bit 0 is the lowest bit, so mask 5 (101) takes indices 0 and 2.",
                        "Sorted: <strong>[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]</strong>.",
                    ],
                    [
                        "n = 0, so <code>1 &lt;&lt; 0</code> = 1 and only mask 0 is tried.",
                        "Mask 0 has no bits and the inner range is empty, giving [].",
                        "One subset is produced.",
                        "The result is <strong>[[]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>mask &gt;&gt; i &amp; 1</code>?",
                     "Shifting right by i moves bit i to the lowest position, and <code>&amp; 1</code> keeps only that bit. In Python <code>&gt;&gt;</code> binds tighter than <code>&amp;</code>, so no brackets are needed."],
                    ["Is this faster than backtracking?",
                     "Same O(n · 2<sup>n</sup>). It avoids recursion, but it cannot prune: backtracking can skip a branch early when a constraint fails, a mask loop cannot."],
                    ["Can bitmasks handle duplicates, as in Subsets II?",
                     "Not directly: masks for [1, 2a] and [1, 2b] give the same subset twice. You would need to deduplicate afterwards, which is why Subsets II uses skipping or counts."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ combination sum
    "combination-sum": {
        "examples": [
            {"call": "sorted(combination_sum([2, 3, 6, 7], 7))", "expect": "[[2, 2, 3], [7]]"},
            {"call": "combination_sum([4, 6], 9)", "expect": "[]"},
        ],
        "approaches": {
            "Sorted candidates, recurse on the same index, break early": {
                "idea": [
                    "A combination is a multiset, so fix an order: pick candidates in non-decreasing index order. Then [2, 2, 3] is built once and [3, 2, 2] never.",
                    "Unlimited reuse means the next pick may be the <em>same</em> index again, so recurse with <code>i</code>, not <code>i + 1</code>.",
                    "Sorting lets the loop stop at the first candidate larger than <code>remaining</code>: every candidate after it is larger too.",
                ],
                "steps": [
                    "Sort <code>candidates</code>. <code>dfs(start, remaining)</code> builds onto <code>path</code>.",
                    "If <code>remaining == 0</code>, record a copy of <code>path</code> and return.",
                    "Loop <code>i</code> from <code>start</code>: if <code>c &gt; remaining</code>, break.",
                    "Otherwise append <code>c</code>, call <code>dfs(i, remaining - c)</code>, then pop it.",
                    "Start with <code>dfs(0, target)</code> and return <code>out</code>.",
                ],
                "why": [
                    "Each combination, written in sorted order, matches exactly one path, because the indices along a path never decrease. So every combination appears once.",
                    "<code>remaining</code> never goes negative, since a candidate is only taken when it fits; a path that cannot reach 0 just runs out of candidates.",
                    "With N candidates, target T and smallest value m, paths are at most T/m deep with up to N branches: <strong>O(N<sup>T/m + 1</sup>)</strong> time in the worst case.",
                    "<code>path</code> and the recursion are at most T/m long: <strong>O(T/m)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "Sorted: [2, 3, 6, 7]. 2 → rem 5 → 2 → rem 3 → 2 → rem 1: every candidate is &gt; 1, break.",
                        "Back at rem 3: try 3 → rem 0, record [2, 2, 3]. Then 6 &gt; 3, break.",
                        "Back at rem 5 (path [2]): 3 → rem 2, then 3 &gt; 2 breaks. 6 &gt; 5 breaks.",
                        "At the top: 3 → rem 4 → 3 → rem 1, dead. 6 → rem 1, dead. 7 → rem 0, record [7].",
                        "The result is <strong>[[2, 2, 3], [7]]</strong>.",
                    ],
                    [
                        "Sorted: [4, 6], target 9.",
                        "4 → rem 5 → 4 → rem 1: 4 &gt; 1, break. Back at rem 5: 6 &gt; 5, break.",
                        "At the top: 6 → rem 3 (start stays at index 1): 6 &gt; 3, break.",
                        "Only even sums are possible, so 9 is never reached.",
                        "The result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>dfs(i, ...)</code> and not <code>dfs(i + 1, ...)</code>?",
                     "Each candidate may be used any number of times. Passing <code>i</code> lets the next level pick the same value again; <code>i + 1</code> would forbid reuse, which is Combination Sum II."],
                    ["Why start the loop at <code>start</code> instead of 0?",
                     "Starting at 0 would let a path go 3 then 2, so [2, 2, 3] would also appear as [2, 3, 2] and [3, 2, 2]. The start index keeps each combination in one canonical order."],
                    ["Is <code>break</code> safe, or should it be <code>continue</code>?",
                     "<code>break</code> is safe only because the list is sorted: once one candidate is too big, all later ones are too. Without the sort you would need <code>continue</code>."],
                ],
            },
            "DP table of combinations per amount": {
                "idea": [
                    "Think of it as coin change that lists the combinations instead of counting them. <code>ways[a]</code> holds every combination summing to amount <code>a</code>.",
                    "Process candidates one at a time in the outer loop. Each combination is then built in candidate order, so [2, 2, 3] is made once and never as [3, 2, 2].",
                    "Iterating amounts upward inside the loop lets a candidate be reused: <code>ways[amount - c]</code> may already contain <code>c</code>.",
                ],
                "steps": [
                    "Create <code>ways</code> with an empty list per amount 0..target, and set <code>ways[0] = [[]]</code>: one way to make 0.",
                    "For each candidate <code>c</code> in sorted order:",
                    "For each <code>amount</code> from <code>c</code> to <code>target</code>, append <code>combo + [c]</code> to <code>ways[amount]</code> for every <code>combo</code> in <code>ways[amount - c]</code>.",
                    "Because amounts go upward, <code>ways[amount - c]</code> already includes combinations that used <code>c</code>, which allows reuse.",
                    "Return <code>ways[target]</code>.",
                ],
                "why": [
                    "After processing candidates c₁..cₖ, <code>ways[a]</code> holds exactly the combinations of those candidates summing to a, each listed once in non-decreasing order. Adding c<sub>k+1</sub> appends it to combinations that already end with values ≤ it.",
                    "No combination is generated twice, since the candidate order fixes where each value is appended.",
                    "N candidates times T amounts, each copying up to K stored combinations: <strong>O(N · T · K)</strong> time.",
                    "Every amount keeps all its combinations: <strong>O(T · K)</strong> space, which can be far more than the answer itself, because it stores partial results for every amount below target too.",
                ],
                "dry": [
                    [
                        "c=2: ways[2]=[[2]], ways[4]=[[2,2]], ways[6]=[[2,2,2]]. Odd amounts stay empty.",
                        "c=3: ways[3]=[[3]], ways[5]=[[2,3]], ways[6] gains [3,3], ways[7] gains [2,2,3] from ways[4].",
                        "c=6: ways[6] gains [6]; ways[7] looks at ways[1], which is empty.",
                        "c=7: ways[7] gains [7] from ways[0].",
                        "ways[7] = <strong>[[2, 2, 3], [7]]</strong>.",
                    ],
                    [
                        "c=4: ways[4]=[[4]], ways[8]=[[4,4]]. ways[5], ways[9] look at ways[1], ways[5]: empty.",
                        "c=6: ways[6]=[[6]]. ways[7], ways[8], ways[9] look at ways[1], ways[2], ways[3]: all empty.",
                        "ways[8] stays [[4, 4]]: 4 + 6 = 10 is past the target.",
                        "ways[9] was never filled, so the result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must candidates be the outer loop?",
                     "With amounts outside, each amount would add every candidate in every order, giving permutations: [2, 2, 3], [2, 3, 2] and [3, 2, 2] would all appear."],
                    ["Why do amounts go upward rather than downward?",
                     "Upward lets <code>ways[amount - c]</code> already include <code>c</code>, so the candidate can repeat. Going downward would allow each candidate at most once, as in 0/1 knapsack."],
                    ["When is this better than backtracking?",
                     "Rarely for listing combinations: it builds lists for every amount, even ones never used. It shines when you only need counts, where each <code>ways[a]</code> becomes a single number."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ combination sum II
    "combination-sum-ii": {
        "examples": [
            {"call": "sorted(combination_sum2([10, 1, 2, 7, 6, 1, 5], 8))",
             "expect": "[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]"},
            {"call": "sorted(combination_sum2([2, 5, 2, 1, 2], 5))", "expect": "[[1, 2, 2], [5]]"},
        ],
        "approaches": {
            "Sort, then skip equal siblings": {
                "idea": [
                    "Each element may be used once, so recurse with <code>i + 1</code>. But the input has duplicates, and picking the first 1 or the second 1 would make the same combination twice.",
                    "After sorting, equal values sit side by side. At one level of the recursion, only the <em>first</em> of a run of equal values is tried; the others would start identical subtrees.",
                    "Deeper levels may still take the next equal value, so [1, 1, 6] is allowed: the skip only applies to siblings, not to a parent and child.",
                ],
                "steps": [
                    "Sort into <code>c</code>. <code>dfs(start, remaining)</code> extends <code>path</code>.",
                    "If <code>remaining == 0</code>, record a copy of <code>path</code>.",
                    "Loop <code>i</code> from <code>start</code>. If <code>i &gt; start and c[i] == c[i - 1]</code>, continue: that value was already tried at this level.",
                    "If <code>c[i] &gt; remaining</code>, break: the rest are larger.",
                    "Append <code>c[i]</code>, call <code>dfs(i + 1, remaining - c[i])</code>, pop. Start with <code>dfs(0, target)</code>.",
                ],
                "why": [
                    "Two sibling branches starting with equal values would explore the same multisets, so keeping only the first loses no combination and removes every duplicate.",
                    "The condition <code>i &gt; start</code> keeps the first element of each level eligible, which is how a combination can contain the same value twice.",
                    "The tree has at most 2<sup>n</sup> leaves and copying a path costs up to n: <strong>O(2<sup>n</sup> · n)</strong> time, usually far less thanks to the break.",
                    "Depth and <code>path</code> are at most n: <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "Sorted c = [1, 1, 2, 5, 6, 7, 10], target 8.",
                        "Take 1 (rem 7), take the second 1 (rem 6): 2 → rem 4 dead, 5 → rem 1 dead, 6 → rem 0 records [1, 1, 6], 7 &gt; 6 breaks.",
                        "Still under the first 1: 2 → 5 records [1, 2, 5]; 5 and 6 fail; 7 records [1, 7]; 10 breaks.",
                        "Top level, i=1: c[1] == c[0], skipped, so no second copy of [1, 2, 5] or [1, 7]. Then 2 → 6 records [2, 6]; 5, 6, 7 dead; 10 breaks.",
                        "The result is <strong>[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]</strong>.",
                    ],
                    [
                        "Sorted c = [1, 2, 2, 2, 5], target 5.",
                        "Take 1 (rem 4), take 2 (rem 2), take 2 (rem 0): record [1, 2, 2]. The third 2 at that level is skipped.",
                        "Under [1]: the 2s at i=2 and i=3 are skipped as siblings; 5 &gt; 4 breaks.",
                        "Top: 2 → 2 → rem 1, dead. The other top-level 2s are skipped. 5 → rem 0 records [5].",
                        "The result is <strong>[[1, 2, 2], [5]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>i &gt; start</code> and not <code>i &gt; 0</code>?",
                     "With <code>i &gt; 0</code> the second 1 could never follow the first 1 in a deeper call, so [1, 1, 6] would be lost. Only siblings at the same level are duplicates."],
                    ["Could I use a set of tuples to remove duplicates instead?",
                     "It works but still explores every duplicate subtree, which can be exponentially more work, and needs extra memory for the set."],
                    ["Why must the input be sorted for the skip?",
                     "The check compares <code>c[i]</code> with <code>c[i - 1]</code>, which only catches duplicates when equal values are adjacent. Sorting also enables the early <code>break</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ combinations
    "combinations": {
        "examples": [
            {"call": "combine(4, 2)", "expect": "[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]"},
            {"call": "combine(3, 3)", "expect": "[[1, 2, 3]]"},
        ],
        "approaches": {
            "Backtracking with an upper bound on the next choice": {
                "idea": [
                    "Choose numbers in increasing order, so each k-element combination is built once.",
                    "If <code>path</code> still needs <code>k - len(path)</code> numbers, the next one can be at most <code>n - (k - len(path)) + 1</code>; anything larger leaves too few numbers after it.",
                    "That bound prunes every branch that would run out of numbers, so every leaf the recursion reaches is a real answer.",
                ],
                "steps": [
                    "<code>dfs(start)</code>: if <code>len(path) == k</code>, record a copy and return.",
                    "Compute <code>last = n - (k - len(path)) + 1</code>, the largest value that still leaves room for the rest.",
                    "For each <code>v</code> from <code>start</code> to <code>last</code>: append <code>v</code>.",
                    "Recurse with <code>dfs(v + 1)</code>, so later numbers are larger.",
                    "Pop <code>v</code> and try the next one. Start with <code>dfs(1)</code>.",
                ],
                "why": [
                    "Increasing order gives each combination exactly one path, so no duplicates and nothing missed.",
                    "If the bound holds, at least <code>k - len(path) - 1</code> numbers remain after <code>v</code>, enough to finish; so no branch dead-ends.",
                    "There are C(n, k) leaves and each costs O(k) to copy: <strong>O(k · C(n, k))</strong> time.",
                    "<code>path</code> and the recursion depth are at most k: <strong>O(k)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "dfs(1): path is empty, last = 4 − 2 + 1 = 3, so v runs 1..3 (4 cannot start a pair).",
                        "v=1: dfs(2), last = 4 − 1 + 1 = 4: records [1, 2], [1, 3], [1, 4].",
                        "v=2: dfs(3) records [2, 3], [2, 4].",
                        "v=3: dfs(4) records [3, 4].",
                        "The result is <strong>[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]</strong>.",
                    ],
                    [
                        "dfs(1): last = 3 − 3 + 1 = 1, so only v=1 is tried.",
                        "dfs(2): last = 3 − 2 + 1 = 2, only v=2. dfs(3): last = 3, only v=3.",
                        "No branch is wasted: without the bound, starting with 2 or 3 would be tried and fail.",
                        "The result is <strong>[[1, 2, 3]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Where does <code>n - (k - len(path)) + 1</code> come from?",
                     "If r numbers are still needed, the next one v must leave r − 1 numbers above it: v + (r − 1) ≤ n, so v ≤ n − r + 1."],
                    ["Is the bound needed for correctness?",
                     "No. Without it the recursion still returns the right answer; it just explores branches that can never reach length k, which is wasted time when k is close to n."],
                    ["Why <code>dfs(v + 1)</code> rather than <code>dfs(start + 1)</code>?",
                     "The next number must be larger than the one just chosen. Using <code>start + 1</code> would allow, say, 3 then 2."],
                ],
            },
            "itertools.combinations": {
                "idea": [
                    "Python's standard library already enumerates k-element combinations of an iterable in lexicographic order.",
                    "Feed it <code>range(1, n + 1)</code> and convert each tuple to a list.",
                    "Inside, it does the same thing as the backtracking: keeps k increasing indices and advances the rightmost one that can still move.",
                ],
                "steps": [
                    "Call <code>itertools.combinations(range(1, n + 1), k)</code>.",
                    "It yields tuples in lexicographic order: (1, 2), (1, 3), ...",
                    "Convert each tuple with <code>list(c)</code>, since the problem expects lists.",
                    "Return the list of lists.",
                ],
                "why": [
                    "The library is defined to yield every k-length combination of the input positions exactly once.",
                    "C(n, k) results, each of size k: <strong>O(k · C(n, k))</strong> time.",
                    "The generator keeps k indices: <strong>O(k)</strong> extra space beyond the output.",
                    "In an interview it shows you know the library, but expect to be asked to write the recursion.",
                ],
                "dry": [
                    [
                        "Input positions 1, 2, 3, 4, k = 2.",
                        "First index 1 pairs with 2, 3, 4.",
                        "First index 2 pairs with 3, 4; first index 3 pairs with 4.",
                        "Six tuples, converted to lists: <strong>[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]</strong>.",
                    ],
                    [
                        "k equals n = 3, so there is only one way to choose.",
                        "The generator yields (1, 2, 3) and stops.",
                        "It is converted to a list.",
                        "The result is <strong>[[1, 2, 3]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why convert each tuple to a list?",
                     "The expected output is a list of lists, and <code>[1, 2] == (1, 2)</code> is False in Python, so tuples would fail the comparison."],
                    ["What if k &gt; n?",
                     "<code>combinations</code> yields nothing, so the answer is []. The backtracking version also returns [] because its loop range is empty."],
                    ["Is the order guaranteed?",
                     "Yes: combinations come out in lexicographic order of input positions, so sorted input gives sorted output."],
                ],
            },
        },
    },


    # ------------------------------------------------------------------ permutations
    "permutations": {
        "examples": [
            {"call": "sorted(permute([1, 2, 3]))",
             "expect": "[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]"},
            {"call": "sorted(permute([0, -1]))", "expect": "[[-1, 0], [0, -1]]"},
        ],
        "approaches": {
            "Used flags": {
                "idea": [
                    "A permutation fills positions one at a time, and each position can take any element not yet placed.",
                    "A boolean list <code>used</code> records which indices are already in <code>path</code>, so each level loops over all n elements and skips the used ones.",
                    "Order matters here, unlike subsets, so there is no start index: every unused element is a candidate at every level.",
                ],
                "steps": [
                    "Keep <code>out</code>, <code>path</code>, and <code>used = [False] * len(nums)</code>.",
                    "<code>dfs()</code>: if <code>len(path) == len(nums)</code>, record a copy of <code>path</code>.",
                    "Otherwise loop over every index <code>i</code>; skip it if <code>used[i]</code>.",
                    "Choose: set <code>used[i] = True</code> and append <code>x</code>. Explore: call <code>dfs()</code>.",
                    "Un-choose: pop <code>x</code> and set <code>used[i] = False</code> before trying the next index.",
                ],
                "why": [
                    "Level d chooses the element in position d from those still unused, so the paths are exactly the n · (n − 1) · ... · 1 orderings.",
                    "Restoring <code>used[i]</code> after the call is what lets the same element appear in a later position of a different permutation.",
                    "There are n! leaves, each copied in O(n), and each internal node loops over n indices: <strong>O(n · n!)</strong> time.",
                    "<code>path</code>, <code>used</code> and the recursion depth are all O(n): <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "Level 0 picks 1 (used [T, F, F]). Level 1 picks 2, level 2 picks 3: record [1, 2, 3].",
                        "Un-choose 3 and 2. Level 1 picks 3, then level 2 picks 2: record [1, 3, 2].",
                        "Back at level 0, un-choose 1 and pick 2: records [2, 1, 3], [2, 3, 1].",
                        "Pick 3 at level 0: records [3, 1, 2], [3, 2, 1].",
                        "Already in sorted order: <strong>[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]</strong>.",
                    ],
                    [
                        "Level 0 picks 0, level 1 has only −1 left: record [0, −1].",
                        "Un-choose both. Level 0 picks −1, level 1 picks 0: record [−1, 0].",
                        "Output order is [[0, −1], [−1, 0]], following the input order.",
                        "Sorted: <strong>[[-1, 0], [0, -1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why mark by index and not check <code>x in path</code>?",
                     "<code>x in path</code> costs O(n) per check and breaks with duplicate values: the second 1 would look already used. Index flags are O(1) and always exact."],
                    ["Why no start index as in Subsets?",
                     "Subsets ignore order, so a start index avoids repeats. Permutations are all orders, so every unused element must be tried in every position."],
                    ["What happens if I forget <code>used[i] = False</code>?",
                     "The element stays blocked after its branch finishes, so only the first permutation is completed and later branches dead-end."],
                ],
            },
            "Swap into place": {
                "idea": [
                    "Keep the permutation inside the array itself: positions <code>0..i-1</code> are fixed, positions <code>i..n-1</code> are the elements still to place.",
                    "To choose what goes in position <code>i</code>, swap each remaining element into slot <code>i</code> in turn, recurse on <code>i + 1</code>, and swap back.",
                    "No <code>used</code> list or <code>path</code> is needed, because the unused elements are exactly the suffix.",
                ],
                "steps": [
                    "Copy the input (<code>nums = nums[:]</code>) so the caller's list is untouched.",
                    "<code>dfs(i)</code>: if <code>i == len(nums)</code>, record a copy of <code>nums</code>.",
                    "For each <code>j</code> from <code>i</code> to the end, swap <code>nums[i]</code> and <code>nums[j]</code>: element j now sits in slot i.",
                    "Recurse with <code>dfs(i + 1)</code>.",
                    "Swap the same pair back so the suffix is restored before the next <code>j</code>.",
                ],
                "why": [
                    "Every element of the suffix gets a turn in slot <code>i</code>, and the swap-back restores the array exactly, so each level sees the same suffix for each choice.",
                    "By induction each call produces every ordering of its suffix once, giving all n! permutations.",
                    "n! leaves, each copied in O(n): <strong>O(n · n!)</strong> time.",
                    "Only the recursion stack of depth n: <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "i=0, j=0: no change [1, 2, 3]. Inside, i=1 gives [1, 2, 3] then, swapping 2 and 3, [1, 3, 2].",
                        "i=0, j=1: swap gives [2, 1, 3]; records [2, 1, 3] and [2, 3, 1]; swap back to [1, 2, 3].",
                        "i=0, j=2: swap 1 and 3 gives [3, 2, 1]; records [3, 2, 1] and then [3, 1, 2].",
                        "The last two come out of lexicographic order, which is why the call sorts.",
                        "Sorted: <strong>[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]</strong>.",
                    ],
                    [
                        "i=0, j=0: [0, −1]; i=1 records [0, −1].",
                        "i=0, j=1: swap gives [−1, 0]; records it, then swaps back.",
                        "The copy means the caller's [0, −1] was never touched.",
                        "Sorted: <strong>[[-1, 0], [0, -1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the output not in lexicographic order?",
                     "Swapping 1 and 3 turns [1, 2, 3] into [3, 2, 1], so the suffix after 3 starts as [2, 1] rather than [1, 2]. Use the used-flags version if the order matters."],
                    ["Why copy <code>nums</code> at the start?",
                     "The swaps happen in place. They are undone by the end, but copying keeps the function free of side effects even if an exception interrupts it."],
                    ["Does the swap trick work with duplicates?",
                     "It produces duplicate permutations. Add a per-level set of values already swapped into slot i to skip repeats."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subsets II
    "subsets-ii": {
        "examples": [
            {"call": "sorted(subsets_with_dup([1, 2, 2]))",
             "expect": "[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]"},
            {"call": "sorted(subsets_with_dup([3, 3, 3]))", "expect": "[[], [3], [3, 3], [3, 3, 3]]"},
        ],
        "approaches": {
            "Sort, skip equal siblings": {
                "idea": [
                    "This is the Subsets recursion with one change: equal values must not start two sibling branches, or the same subset is built twice.",
                    "After sorting, duplicates are adjacent. At each level, try only the first of a run of equal values.",
                    "A deeper level can still take the next copy, so [2, 2] is built once, through the first 2 then the second.",
                ],
                "steps": [
                    "Sort <code>nums</code>. <code>dfs(start)</code> records a copy of <code>path</code> on entry.",
                    "Loop <code>i</code> from <code>start</code> to the end.",
                    "If <code>i &gt; start and nums[i] == nums[i - 1]</code>, continue: this value was already tried at this level.",
                    "Otherwise append <code>nums[i]</code>, call <code>dfs(i + 1)</code>, and pop.",
                    "Call <code>dfs(0)</code> and return <code>out</code>.",
                ],
                "why": [
                    "Choosing the first or the second of two equal values at the same level leads to identical sets of subsets, so exploring only the first keeps every distinct subset and drops every repeat.",
                    "A value with count c can appear 0..c times: the path takes copies in order, one per level, so each multiplicity is reached once.",
                    "At most 2<sup>n</sup> nodes, each copying up to n values: <strong>O(n · 2<sup>n</sup>)</strong> time.",
                    "Recursion and <code>path</code> are at most n deep: <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "dfs(0) records []. i=0 takes 1: dfs(1) records [1].",
                        "dfs(1): i=1 takes 2 → records [1, 2], and inside takes the second 2 → [1, 2, 2]. i=2 is skipped: equal to nums[1] and i &gt; start.",
                        "dfs(0): i=1 takes 2 → records [2], then [2, 2]. i=2 is skipped.",
                        "Six subsets, no repeats.",
                        "The result is <strong>[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]</strong>.",
                    ],
                    [
                        "dfs(0) records []. i=0 takes 3 → [3], then 3 → [3, 3], then 3 → [3, 3, 3].",
                        "At every level, the later 3s are skipped as siblings.",
                        "Without the skip there would be 8 subsets; with it, one per count 0..3.",
                        "The result is <strong>[[], [3], [3, 3], [3, 3, 3]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>i &gt; start</code> not block [2, 2]?",
                     "The second 2 is taken at a deeper level, where it is the first index tried (<code>i == start</code>), so the check does not apply."],
                    ["Can I skip the sort?",
                     "No. The duplicate check only compares neighbours, and unsorted input like [2, 1, 2] keeps the two 2s apart."],
                    ["Would converting results to a set of tuples work?",
                     "Only after sorting each subset, and it still explores all 2<sup>n</sup> branches. Skipping avoids the work entirely."],
                ],
            },
            "Counts per distinct value": {
                "idea": [
                    "With duplicates, a subset is really a choice of <em>how many</em> copies of each distinct value to take.",
                    "A value with count c offers c + 1 options: 0, 1, ..., c copies. Extending every partial subset with each option gives all subsets without any repeats.",
                    "It is the iterative doubling idea, where each value multiplies the list by (count + 1) instead of 2.",
                ],
                "steps": [
                    "Start with <code>out = [[]]</code>.",
                    "Loop over <code>sorted(Counter(nums).items())</code>, giving each distinct <code>value</code> and its <code>count</code>.",
                    "Replace <code>out</code> with <code>[s + [value] * k for s in out for k in range(count + 1)]</code>.",
                    "After the last value, return <code>out</code>.",
                ],
                "why": [
                    "Distinct subsets of a multiset correspond one-to-one to tuples of copy counts, and the comprehension produces each tuple once.",
                    "Each subset lists values in sorted order because the distinct values are processed in sorted order.",
                    "The number of subsets is at most 2<sup>n</sup> and each is up to n long: <strong>O(n · 2<sup>n</sup>)</strong> time.",
                    "Besides the output, only the Counter of distinct values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Counter gives (1, 1), (2, 2).",
                        "value 1, k ∈ {0, 1}: out = [[], [1]].",
                        "value 2, k ∈ {0, 1, 2}: from [] → [], [2], [2, 2]; from [1] → [1], [1, 2], [1, 2, 2].",
                        "Sorted: <strong>[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]</strong>.",
                    ],
                    [
                        "Counter gives (3, 3).",
                        "One step: k ∈ {0, 1, 2, 3} from [].",
                        "out = [[], [3], [3, 3], [3, 3, 3]].",
                        "The result is <strong>[[], [3], [3, 3], [3, 3, 3]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>range(count + 1)</code>?",
                     "Zero copies is a valid option. <code>range(count)</code> would forbid using every copy, losing [2, 2] for two 2s."],
                    ["Why sort the Counter items?",
                     "Not for correctness of the set, but so each subset's values come out in sorted order and the result is deterministic."],
                    ["Is this faster than the recursion?",
                     "Same order, but it never creates a duplicate branch at all, so with many repeated values it does noticeably less work."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ permutations II
    "permutations-ii": {
        "examples": [
            {"call": "sorted(permute_unique([1, 1, 2]))", "expect": "[[1, 1, 2], [1, 2, 1], [2, 1, 1]]"},
            {"call": "permute_unique([2, 2, 2])", "expect": "[[2, 2, 2]]"},
        ],
        "approaches": {
            "Sort, skip a duplicate whose twin is unused": {
                "idea": [
                    "Equal values are interchangeable, so swapping the two 1s in a permutation gives the same list. Fix an order among equal values to count each arrangement once.",
                    "The rule: after sorting, a copy may only be placed if the copy just before it is already placed. Equal values then always enter <code>path</code> left to right.",
                    "This is the used-flags permutation with one extra skip condition.",
                ],
                "steps": [
                    "Sort <code>nums</code>; keep <code>path</code> and <code>used</code>.",
                    "<code>dfs()</code>: when <code>path</code> is full, record a copy.",
                    "For each <code>i</code>: skip if <code>used[i]</code>.",
                    "Also skip if <code>i &gt; 0 and nums[i] == nums[i - 1] and not used[i - 1]</code>: its earlier twin has not been placed yet.",
                    "Otherwise choose (mark, append), recurse, un-choose (pop, unmark).",
                ],
                "why": [
                    "Among the orderings of equal copies, exactly one places them in index order, so each distinct permutation is produced exactly once.",
                    "The skip also cuts whole subtrees early: at the top level, the second 1 is never tried as the first element.",
                    "At most n · n! work as for plain permutations, far less with many duplicates: <strong>O(n · n!)</strong> time.",
                    "<code>used</code>, <code>path</code> and recursion are O(n): <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "Sorted [1, 1, 2]. Level 0 takes index 0 (1). Level 1: index 1 is allowed because used[0] is True; then 2: record [1, 1, 2].",
                        "Level 1 tries 2 instead, then level 2 takes index 1: record [1, 2, 1].",
                        "Level 0, index 1: nums[1] == nums[0] and used[0] is False, so it is skipped.",
                        "Level 0 takes 2, then the 1s in order: record [2, 1, 1]; the other order is skipped.",
                        "The result is <strong>[[1, 1, 2], [1, 2, 1], [2, 1, 1]]</strong>.",
                    ],
                    [
                        "Level 0 takes index 0. Level 1 takes index 1 (its twin is used), level 2 takes index 2: record [2, 2, 2].",
                        "Every other choice puts a copy before its unused twin and is skipped.",
                        "Only one leaf is reached instead of 6.",
                        "The result is <strong>[[2, 2, 2]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>not used[i - 1]</code> and not <code>used[i - 1]</code>?",
                     "Both versions give correct answers because each fixes some order among copies. <code>not used</code> prunes at the highest level, so it explores fewer nodes."],
                    ["Why must <code>nums</code> be sorted?",
                     "The twin check looks only at <code>nums[i - 1]</code>, so equal values have to be adjacent."],
                    ["What does the skip prevent at the top level?",
                     "Starting with the second 1 while the first is unused would build the same permutations as starting with the first 1."],
                ],
            },
            "Choose from a Counter of remaining values": {
                "idea": [
                    "Instead of tracking indices, track how many copies of each <em>distinct value</em> are left.",
                    "Each level loops over distinct values only, so the two 1s are never separate choices and duplicates cannot arise.",
                ],
                "steps": [
                    "Build <code>counts = Counter(nums)</code>.",
                    "<code>dfs()</code>: when <code>path</code> has <code>len(nums)</code> items, record a copy.",
                    "Loop <code>v</code> over <code>list(counts)</code>; skip values whose count is 0.",
                    "Choose: decrement <code>counts[v]</code>, append <code>v</code>. Explore: <code>dfs()</code>.",
                    "Un-choose: pop and increment <code>counts[v]</code>.",
                ],
                "why": [
                    "Each level picks a distinct value, so two branches at a level always differ in that position; the leaves are all distinct.",
                    "Every arrangement is reachable, because any available value can go in any position.",
                    "With P distinct permutations, the work is about <strong>O(n · P)</strong> time, which can be much less than n · n!.",
                    "The Counter, <code>path</code> and recursion use <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "counts {1: 2, 2: 1}. Take 1 → {1: 1}; take 1 → {1: 0}; take 2: record [1, 1, 2].",
                        "Back under [1]: take 2, then 1: record [1, 2, 1].",
                        "Top level: take 2 → {2: 0}; then 1, 1: record [2, 1, 1].",
                        "Each level loops over just two keys, never over copies.",
                        "The result is <strong>[[1, 1, 2], [1, 2, 1], [2, 1, 1]]</strong>.",
                    ],
                    [
                        "counts {2: 3}. Each level has one key with a positive count.",
                        "Take 2 three times: record [2, 2, 2].",
                        "Unwinding restores counts to 3; no other branch exists.",
                        "The result is <strong>[[2, 2, 2]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why iterate over <code>list(counts)</code>?",
                     "It takes a snapshot of the keys. The loop changes the values in place, and iterating a snapshot avoids any surprise if a key were added."],
                    ["Does this need the input sorted?",
                     "No. The Counter groups equal values itself; sorting would only change the output order."],
                    ["Why is <code>if counts[v]</code> needed?",
                     "Keys stay in the Counter at count 0 once used up; the check stops a value being placed more times than it occurs."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ generate parentheses
    "generate-parentheses": {
        "examples": [
            {"call": "sorted(generate_parenthesis(3))",
             "expect": '["((()))", "(()())", "(())()", "()(())", "()()()"]'},
            {"call": "generate_parenthesis(2)", "expect": '["(())", "()()"]'},
        ],
        "approaches": {
            "Add only what keeps the prefix valid": {
                "idea": [
                    "A string is balanced exactly when no prefix has more ')' than '(', and the totals are n each.",
                    "So build left to right and only add a character that keeps the prefix legal: '(' while fewer than n are open, ')' while it would close something.",
                    "Every branch then ends in a valid string; nothing is generated and thrown away.",
                ],
                "steps": [
                    "<code>dfs(open_, close)</code> tracks how many of each are in <code>path</code>.",
                    "If <code>len(path) == 2 * n</code>, join and record it.",
                    "If <code>open_ &lt; n</code>, append '(', recurse with <code>open_ + 1</code>, pop.",
                    "If <code>close &lt; open_</code>, append ')', recurse with <code>close + 1</code>, pop.",
                    "Start with <code>dfs(0, 0)</code>.",
                ],
                "why": [
                    "The two conditions are exactly the prefix rules of a balanced string, so every valid string has a path and every path is valid.",
                    "At length 2n, <code>open_ == n</code> and <code>close == open_</code>, so the string is complete and balanced.",
                    "The number of results is the Catalan number, about 4<sup>n</sup>/n<sup>1.5</sup>, each costing O(n) to join: <strong>O(4<sup>n</sup> / √n)</strong> time.",
                    "Depth and <code>path</code> are 2n: <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "Always try '(' first: ((( then ))) gives \"((()))\".",
                        "Back at \"((\": close one, then open: \"(()\" → \"(()(\" → \"(()())\".",
                        "\"(()\" closing again → \"(())\" → \"(())()\".",
                        "Back at \"(\": close → \"()\" → \"()(\" leads to \"()(())\" and \"()()()\".",
                        "Already sorted, since '(' sorts before ')': <strong>[\"((()))\", \"(()())\", \"(())()\", \"()(())\", \"()()()\"]</strong>.",
                    ],
                    [
                        "dfs(0,0) → '(' → dfs(1,0) → '(' → dfs(2,0): only ')' allowed twice: \"(())\".",
                        "Back at dfs(1,0): ')' → dfs(1,1): close &lt; open fails, open &lt; 2 succeeds: \"()(\" → \"()()\".",
                        "At dfs(0,0) the ')' branch is refused because close is not less than open.",
                        "The result is <strong>[\"(())\", \"()()\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>close &lt; open_</code> and not <code>close &lt; n</code>?",
                     "<code>close &lt; n</code> would allow \")(\" at the start. Closing is only legal when something is open."],
                    ["Does any branch ever fail?",
                     "No. Every partial string can be completed: add the missing '(' and then close everything. That is why there is no validity check at the end."],
                    ["Why is the count a Catalan number?",
                     "Balanced strings of n pairs are a classic Catalan family: 1, 2, 5, 14, 42 for n = 1..5."],
                ],
            },
            "Generate all 2<sup>2n</sup> strings, keep the valid ones": {
                "idea": [
                    "Brute force: every string of length 2n over '(' and ')' is a candidate; keep those that are balanced.",
                    "A string is balanced when a running counter never drops below 0 and ends at 0.",
                    "It is the baseline that shows why pruning while building is worth it.",
                ],
                "steps": [
                    "Generate candidates with <code>itertools.product(\"()\", repeat=2 * n)</code> and join each to a string.",
                    "<code>valid(s)</code>: add 1 for '(' and subtract 1 for ')', returning False the moment <code>balance &lt; 0</code>.",
                    "At the end, the string is valid only if <code>balance == 0</code>.",
                    "Return the candidates that pass.",
                ],
                "why": [
                    "A string is balanced exactly when every prefix has balance ≥ 0 and the total is 0, which is what <code>valid</code> checks.",
                    "All 2<sup>2n</sup> = 4<sup>n</sup> strings are checked in O(n) each: <strong>O(n · 4<sup>n</sup>)</strong> time.",
                    "The generator and checker keep one string at a time: <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "product yields 64 strings, from \"((((((\" to \"))))))\".",
                        "Strings like \"((((((\" pass the prefix test but end with balance 6: rejected.",
                        "Strings starting with ')' fail on the first character.",
                        "Five survive, already in sorted order: <strong>[\"((()))\", \"(()())\", \"(())()\", \"()(())\", \"()()()\"]</strong>.",
                    ],
                    [
                        "product yields 16 strings of length 4.",
                        "\"((((\", \"((()\", \"(()(\" end with positive balance; \"())(\" drops to −1 at the third character.",
                        "Only \"(())\" and \"()()\" reach 0 without dipping below it.",
                        "The result is <strong>[\"(())\", \"()()\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["How much work is wasted?",
                     "For n = 3, 64 strings are built and 5 kept; for n = 10, about a million are built and 16796 kept."],
                    ["Why check <code>balance &lt; 0</code> inside the loop?",
                     "A string like \")(\" ends with balance 0 but is not valid. The prefix check catches it."],
                    ["Why is the output in sorted order?",
                     "<code>product</code> follows the order of \"()\", which matches ASCII order since '(' sorts before ')'."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word search
    "word-search": {
        "examples": [
            {"setup": WORD_BOARD, "call": 'exist(board, "ABCCED")', "expect": "True"},
            {"setup": WORD_BOARD, "call": 'exist(board, "ABCF")', "expect": "False"},
        ],
        "approaches": {
            "DFS with in-place marking and pruning": {
                "idea": [
                    "Try every cell as the start, and from a matching cell walk to a neighbour that matches the next letter: a depth-first search over paths.",
                    "A cell may be used once per path, so mark it with '#' while it is on the path and restore the letter when the search backs out.",
                    "Two cheap prunes run first: if the board lacks enough of some letter, answer False at once; and if the first letter is more common than the last, search the reversed word to start from fewer cells.",
                ],
                "steps": [
                    "Count the board's letters in <code>have</code>. If any letter of <code>word</code> is needed more times than <code>have</code> provides, return False.",
                    "If <code>have[word[0]] &gt; have[word[-1]]</code>, reverse <code>word</code>.",
                    "<code>dfs(r, c, i)</code>: return False if <code>board[r][c] != word[i]</code>; return True if <code>i</code> is the last index.",
                    "Mark <code>board[r][c] = \"#\"</code> and try the four neighbours inside the grid with <code>i + 1</code>; <code>any</code> stops at the first success.",
                    "Restore <code>board[r][c] = word[i]</code> and return the result. The answer is <code>any(dfs(r, c, 0))</code> over all cells.",
                ],
                "why": [
                    "Every path of distinct adjacent cells spelling the word is explored from its first cell, and marking forbids revisiting, so the search is exact.",
                    "A path spells the word exactly when it spells the reversed word backwards, so the reversal never changes the answer.",
                    "Each of the R · C starts branches into at most 3 new directions per letter (the 4th is where it came from): <strong>O(R · C · 3<sup>L</sup>)</strong> time.",
                    "The recursion is at most L deep and marking reuses the board: <strong>O(L)</strong> space, plus O(R · C) letters counted once.",
                ],
                "dry": [
                    [
                        "have[A] = 2 &gt; have[D] = 1, so the search uses \"DECCBA\".",
                        "Cells (0,0)..(2,0) fail at once; only (2,1) is 'D'.",
                        "From D(2,1): F(1,1) is not 'E', E(2,2) is. From E: C(1,2), then C(0,2).",
                        "From C(0,2): (1,2) is '#', E(0,3) is not 'B', B(0,1) is. From B: F fails, (0,2) is '#', A(0,0) matches the last letter.",
                        "The path returns True and every cell is restored: <strong>True</strong>.",
                    ],
                    [
                        "Counts are enough, and have[A] = 2 &gt; have[F] = 1, so the search uses \"FCBA\".",
                        "Only (1,1) is 'F'. Its neighbours: D, B fail; C(1,2) matches.",
                        "From C(1,2): E(2,2), C(0,2), S(1,3) are not 'B' and (1,1) is '#'. Back at F, S(1,0) fails.",
                        "Every other start cell is not 'F'.",
                        "No path exists: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why mark with '#' instead of keeping a visited set?",
                     "It avoids an extra structure and hashing. Restoring the letter afterwards matters: the tests check the board is unchanged."],
                    ["What does the letter count catch that DFS would not?",
                     "\"ABCB\" needs two B's and the board has one: it returns False immediately. On a 6 × 6 board of 'a' with word \"aaa…ab\", DFS would otherwise explore an enormous number of paths."],
                    ["Why can the word be reversed safely?",
                     "Paths are undirected sequences of cells, so a path for the word read backwards is a path for the reversed word. Starting from the rarer letter means fewer DFS roots."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ palindrome partitioning
    "palindrome-partitioning": {
        "examples": [
            {"call": 'sorted(partition("aab"))', "expect": '[["a", "a", "b"], ["aa", "b"]]'},
            {"call": 'partition("aba")', "expect": '[["a", "b", "a"], ["aba"]]'},
        ],
        "approaches": {
            "Precomputed palindrome table + backtracking": {
                "idea": [
                    "A partition is a sequence of cut points. From position <code>i</code>, the next piece is <code>s[i..j]</code> for some <code>j</code>, and it must be a palindrome.",
                    "Many pieces are tested repeatedly across branches, so precompute <code>pal[i][j]</code> for every substring in O(n²) and make each test O(1).",
                    "Then backtrack: choose a palindromic piece, recurse on the rest, un-choose.",
                ],
                "steps": [
                    "Fill <code>pal</code> with <code>i</code> going from n − 1 down to 0: <code>pal[i][j] = s[i] == s[j] and (j - i &lt; 2 or pal[i + 1][j - 1])</code>.",
                    "<code>dfs(i)</code>: if <code>i == n</code>, record a copy of <code>path</code>.",
                    "For each <code>j</code> from <code>i</code> to n − 1, if <code>pal[i][j]</code>, append <code>s[i:j + 1]</code>.",
                    "Recurse with <code>dfs(j + 1)</code>, then pop.",
                    "Start with <code>dfs(0)</code>.",
                ],
                "why": [
                    "Each partition is a unique sequence of palindromic pieces covering s left to right, and the recursion enumerates exactly those sequences.",
                    "Filling <code>i</code> downwards guarantees <code>pal[i + 1][j - 1]</code> is ready when <code>pal[i][j]</code> needs it.",
                    "There can be 2<sup>n−1</sup> partitions (all one letter repeated), each costing O(n) to build: <strong>O(n · 2<sup>n</sup>)</strong> time.",
                    "The table is <strong>O(n²)</strong> space; the recursion adds O(n).",
                ],
                "dry": [
                    [
                        "Table: single letters are True, pal[0][1] (\"aa\") is True, pal[1][2] (\"ab\") and pal[0][2] (\"aab\") are False.",
                        "dfs(0): j=0 takes \"a\" → dfs(1): j=1 takes \"a\" → dfs(2): \"b\" → record [a, a, b]. j=2 \"ab\" is not a palindrome.",
                        "dfs(0): j=1 takes \"aa\" → dfs(2): \"b\" → record [aa, b].",
                        "dfs(0): j=2 \"aab\" is rejected.",
                        "The result is <strong>[[\"a\", \"a\", \"b\"], [\"aa\", \"b\"]]</strong>.",
                    ],
                    [
                        "Table: pal[0][1] \"ab\" and pal[1][2] \"ba\" are False; pal[0][2] is s[0] == s[2] and pal[1][1], so True.",
                        "dfs(0): \"a\" → dfs(1): \"b\" → dfs(2): \"a\" → record [a, b, a]. \"ba\" is rejected.",
                        "dfs(0): \"ab\" is rejected; \"aba\" → dfs(3) records [aba].",
                        "The result is <strong>[[\"a\", \"b\", \"a\"], [\"aba\"]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>i</code> go from n − 1 down to 0 when building the table?",
                     "<code>pal[i][j]</code> depends on <code>pal[i + 1][j - 1]</code>, a row below. Filling bottom-up makes sure that row is finished."],
                    ["What is <code>j - i &lt; 2</code> for?",
                     "Pieces of length 1 or 2 have no inner substring to check: they are palindromes when their end letters match."],
                    ["Is the O(n²) table worth it?",
                     "Yes when n is moderate: without it every candidate piece is reversed and compared again in every branch that reaches it."],
                ],
            },
            "Check each piece by slicing": {
                "idea": [
                    "The same backtracking, but test each candidate piece directly with <code>piece == piece[::-1]</code>.",
                    "Simpler to write and no table, at the cost of an O(n) check every time a piece is tried.",
                ],
                "steps": [
                    "<code>dfs(i)</code>: if <code>i == len(s)</code>, record a copy of <code>path</code>.",
                    "For each end <code>j</code> from <code>i + 1</code> to <code>len(s)</code>, slice <code>piece = s[i:j]</code>.",
                    "If <code>piece == piece[::-1]</code>, append it, call <code>dfs(j)</code>, pop.",
                    "Start with <code>dfs(0)</code>.",
                ],
                "why": [
                    "The search tree is identical to the table version; only the palindrome test differs, so the results are the same.",
                    "Each node tries up to n pieces, each costing O(n) to slice and reverse: <strong>O(n² · 2<sup>n</sup>)</strong> time.",
                    "Only the recursion and <code>path</code>: <strong>O(n)</strong> space beyond the output.",
                    "Here <code>j</code> is an exclusive end, so the recursion continues at <code>dfs(j)</code> rather than <code>j + 1</code>.",
                ],
                "dry": [
                    [
                        "dfs(0): \"a\" is a palindrome → dfs(1): \"a\" → dfs(2): \"b\" → record [a, a, b]. \"ab\" fails.",
                        "dfs(0): \"aa\" → dfs(2): \"b\" → record [aa, b].",
                        "dfs(0): \"aab\" reversed is \"baa\": rejected.",
                        "The result is <strong>[[\"a\", \"a\", \"b\"], [\"aa\", \"b\"]]</strong>.",
                    ],
                    [
                        "dfs(0): \"a\" → dfs(1): \"b\" → dfs(2): \"a\" → record [a, b, a]. \"ba\" fails.",
                        "dfs(0): \"ab\" fails; \"aba\" equals its reverse → record [aba].",
                        "Same tree as the table version.",
                        "The result is <strong>[[\"a\", \"b\", \"a\"], [\"aba\"]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>range(i + 1, len(s) + 1)</code>?",
                     "<code>j</code> is a slice end, which is exclusive, so it must reach <code>len(s)</code> for the last piece to include the final character."],
                    ["When is this good enough?",
                     "For short strings the extra factor of n hardly matters, and the code is shorter and easier to get right."],
                    ["Could I cache the checks instead of building a table?",
                     "Yes, <code>@cache</code> on a function of (i, j) gives the same O(1) repeat checks, filled lazily."],
                ],
            },
        },
    },


    # ------------------------------------------------------------------ restore IP addresses
    "restore-ip-addresses": {
        "examples": [
            {"call": 'sorted(restore_ip_addresses("25525511135"))',
             "expect": '["255.255.11.135", "255.255.111.35"]'},
            {"call": 'restore_ip_addresses("010010")', "expect": '["0.10.0.10", "0.100.1.0"]'},
        ],
        "approaches": {
            "Backtracking with length bounds": {
                "idea": [
                    "An address is four parts, each 1 to 3 digits, between 0 and 255, with no leading zero unless the part is exactly \"0\". Choose the parts one at a time.",
                    "With <code>left</code> parts still to place, the remaining digits must number between <code>left</code> and <code>3 * left</code>; outside that window the branch is hopeless and is cut at once.",
                    "Trying sizes 1, 2, 3 in order, a part that is too short, has a leading zero or exceeds 255 can only get worse if made longer, so the loop breaks.",
                ],
                "steps": [
                    "<code>dfs(i)</code>: <code>left = 4 - len(parts)</code>. If <code>left == 0</code>, record <code>\".\".join(parts)</code> when <code>i == len(s)</code>, and return either way.",
                    "If <code>len(s) - i</code> is not between <code>left</code> and <code>3 * left</code>, return.",
                    "For <code>size</code> in 1, 2, 3, take <code>seg = s[i:i + size]</code>.",
                    "Break if <code>seg</code> is shorter than <code>size</code> (out of digits), starts with '0' and is longer than 1, or is above 255.",
                    "Otherwise append <code>seg</code>, call <code>dfs(i + size)</code>, pop.",
                ],
                "why": [
                    "Every valid address is four valid parts that use all digits, and the recursion tries every valid part size at every step, so none is missed; invalid parts are never appended.",
                    "The break is safe: once a part has a leading zero or exceeds 255, every longer part starting at the same digit does too.",
                    "There are at most 3<sup>4</sup> = 81 paths, whatever the input, and strings longer than 12 digits are rejected by the bound: <strong>O(1)</strong> time.",
                    "At most four parts and four frames: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "11 digits. \"2\" leaves 10 digits for 3 parts (max 9): pruned. \"25\" → \"5\" or \"52\" leave too many: pruned; \"525\" &gt; 255 breaks.",
                        "\"255\" → \"2\" pruned; \"25\" → \"5\" and \"51\" leave too many; \"511\" breaks.",
                        "\"255\".\"255\" → \"1\" leaves 4 digits for 1 part: pruned. \"11\" → last part \"1\" or \"13\" leave digits unused; \"135\" uses all: record.",
                        "\"255\".\"255\".\"111\" → \"3\" leaves one digit; \"35\" uses all: record. The size-3 slice is only \"35\", too short: break.",
                        "Sorted: <strong>[\"255.255.11.135\", \"255.255.111.35\"]</strong>.",
                    ],
                    [
                        "Part 1: \"0\". Size 2 gives \"01\", a leading zero: break, so the first part is always \"0\".",
                        "\"0\".\"1\" → \"0\" → \"0\" leaves a digit unused; \"01\" breaks. Then part 3 \"00\" breaks.",
                        "\"0\".\"10\" → \"0\" → \"1\" leaves a digit; \"10\" uses all: record 0.10.0.10. \"01\" breaks.",
                        "\"0\".\"100\" → \"1\" → \"0\": record 0.100.1.0. \"10\" as part 3 leaves no digits: pruned. \"10\" (slice of 2) is too short for size 3: break.",
                        "The result is <strong>[\"0.10.0.10\", \"0.100.1.0\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>break</code> rather than <code>continue</code> on a bad part?",
                     "A longer part starting at the same position keeps the leading zero, is even larger, or runs further past the end. No later size can be valid."],
                    ["Why is \"0\" allowed but \"01\" not?",
                     "IPv4 parts are written without leading zeros. The check <code>size &gt; 1 and seg[0] == \"0\"</code> blocks only multi-digit parts that start with 0."],
                    ["Why call this O(1)?",
                     "Four parts of at most three digits bound the search to 81 paths, and any input longer than 12 digits is rejected straight away by the length bound."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ letter combinations of a phone number
    "letter-combinations-phone": {
        "examples": [
            {"call": 'sorted(letter_combinations("23"))',
             "expect": '["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]'},
            {"call": 'letter_combinations("")', "expect": "[]"},
        ],
        "approaches": {
            "Backtracking one digit at a time": {
                "idea": [
                    "Each digit maps to 3 or 4 letters, and a combination picks one letter per digit, in order.",
                    "Recurse over the digits: at position <code>i</code>, try each letter of <code>KEYS[digits[i]]</code>, recurse on <code>i + 1</code>, and pop.",
                    "An empty input is a special case: the problem wants [], not [\"\"].",
                ],
                "steps": [
                    "If <code>digits</code> is empty, return [].",
                    "<code>dfs(i)</code>: if <code>i == len(digits)</code>, join <code>path</code> and record it.",
                    "Otherwise loop <code>ch</code> over <code>KEYS[digits[i]]</code>.",
                    "Append <code>ch</code>, call <code>dfs(i + 1)</code>, pop.",
                    "Call <code>dfs(0)</code> and return <code>out</code>.",
                ],
                "why": [
                    "The answer is the Cartesian product of the letter groups, and the recursion builds each element of the product once.",
                    "Up to 4<sup>n</sup> combinations of length n, each joined in O(n): <strong>O(n · 4<sup>n</sup>)</strong> time.",
                    "<code>path</code> and the recursion depth are n: <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "KEYS[\"2\"] = \"abc\", KEYS[\"3\"] = \"def\".",
                        "i=0 picks a; i=1 picks d, e, f: records ad, ae, af.",
                        "i=0 picks b: records bd, be, bf. Picks c: cd, ce, cf.",
                        "Nine combinations, already in sorted order.",
                        "The result is <strong>[\"ad\", \"ae\", \"af\", \"bd\", \"be\", \"bf\", \"cd\", \"ce\", \"cf\"]</strong>.",
                    ],
                    [
                        "<code>digits</code> is empty, so the guard fires.",
                        "Without it, <code>dfs(0)</code> would see <code>i == len(digits)</code> and record \"\".",
                        "The problem defines no combinations for no digits.",
                        "The result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the special case for an empty string?",
                     "The recursion would return [\"\"], one empty combination, but the expected answer is []."],
                    ["Why is the bound 4<sup>n</sup> rather than 3<sup>n</sup>?",
                     "Digits 7 and 9 have four letters (pqrs, wxyz), so the worst case is four choices per digit."],
                    ["Why use a list <code>path</code> instead of string concatenation?",
                     "Appending and popping a list is O(1); passing <code>prefix + ch</code> also works and is simpler, but creates a new string at every node."],
                ],
            },
            "itertools.product": {
                "idea": [
                    "The answer is exactly the Cartesian product of the letter strings for each digit.",
                    "<code>itertools.product</code> computes that product, yielding tuples of letters in order.",
                ],
                "steps": [
                    "Return [] if <code>digits</code> is empty.",
                    "Build the letter strings <code>KEYS[d]</code> for each digit and unpack them into <code>itertools.product</code>.",
                    "Join each tuple into a string.",
                    "Return the list of strings.",
                ],
                "why": [
                    "<code>product</code> yields every tuple with one item from each input exactly once, in lexicographic order of positions.",
                    "Up to 4<sup>n</sup> tuples, each joined in O(n): <strong>O(n · 4<sup>n</sup>)</strong> time.",
                    "The generator holds one tuple at a time: <strong>O(n)</strong> space beyond the output.",
                    "It is the same algorithm as the recursion, with the loop handled by the library.",
                ],
                "dry": [
                    [
                        "Inputs: \"abc\", \"def\".",
                        "product yields (a,d), (a,e), (a,f), then (b,…), then (c,…).",
                        "Joining gives nine strings in sorted order.",
                        "The result is <strong>[\"ad\", \"ae\", \"af\", \"bd\", \"be\", \"bf\", \"cd\", \"ce\", \"cf\"]</strong>.",
                    ],
                    [
                        "<code>digits</code> is empty, so the guard returns at once.",
                        "Without it, <code>product()</code> with no inputs yields one empty tuple.",
                        "That would give [\"\"].",
                        "The result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the empty guard still needed here?",
                     "<code>itertools.product()</code> with no arguments yields a single empty tuple, which would become [\"\"]."],
                    ["What does the <code>*</code> in <code>product(*(...))</code> do?",
                     "It unpacks the generator so each digit's letter string becomes a separate argument to <code>product</code>."],
                    ["Will an interviewer accept this?",
                     "As a follow-up, yes; they will usually want to see the recursion first, since it is the backtracking pattern being tested."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ matchsticks to square
    "matchsticks-to-square": {
        "examples": [
            {"call": "makesquare([1, 1, 2, 2, 2])", "expect": "True"},
            {"call": "makesquare([3, 3, 3, 3, 4])", "expect": "False"},
        ],
        "approaches": {
            "Fill four sides, longest sticks first": {
                "idea": [
                    "Each stick goes on one of four sides, and each side must sum to <code>total / 4</code>. Place sticks one by one, trying each side that still has room.",
                    "Long sticks first: they have the fewest places to go, so dead ends show up near the root instead of deep in the tree.",
                    "Sides with the same current length are interchangeable: if putting a stick on a side of length 3 failed, putting it on another side of length 3 will fail too. The set <code>tried</code> skips those.",
                ],
                "steps": [
                    "Reject at once if there are fewer than 4 sticks or <code>total % 4</code> is non-zero; set <code>side = total // 4</code>.",
                    "Sort the sticks in descending order. If the longest exceeds <code>side</code>, return False.",
                    "<code>dfs(i)</code>: if every stick is placed, return True.",
                    "For each side <code>k</code>: if <code>sides[k] + sticks[i] &lt;= side</code> and <code>sides[k]</code> is not in <code>tried</code>, add it to <code>tried</code>, place the stick and recurse; return True on success, otherwise remove it.",
                    "If no side works, return False.",
                ],
                "why": [
                    "No side ever exceeds <code>side</code>, and the total is exactly 4 · side, so when all sticks are placed every side equals <code>side</code>.",
                    "Skipping a side whose length was already tried loses nothing, because the two states are the same up to renaming the sides.",
                    "Each stick has up to 4 choices: <strong>O(4<sup>n</sup>)</strong> in the worst case, far less with the pruning.",
                    "The recursion is n deep and <code>tried</code> holds at most 4 values per level: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "total 8, side 2; sticks sorted [2, 2, 2, 1, 1].",
                        "2 → side 0 (tried {0}, so sides 1–3 are not tried for it). 2 → side 1 (side 0 is full). 2 → side 2.",
                        "1 → side 3 (sides 0–2 full). 1 → side 3 again, making [2, 2, 2, 2].",
                        "All sticks placed with no backtracking.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "total 16, side 4; sticks [4, 3, 3, 3, 3].",
                        "4 → side 0. The 3s go to sides 1, 2, 3 (each new side has length 0, so only the first empty one is tried).",
                        "The last 3 fits nowhere: [4, 3, 3, 3] has no room. Undo; every alternative is a side of the same length already tried.",
                        "Unwinding to the top, the 4 cannot go on another empty side either (0 is in <code>tried</code>).",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort in descending order?",
                     "A long stick has few legal sides, so it fails fast. Placing small sticks first fills sides in many ways before discovering that a long stick fits nowhere."],
                    ["What exactly does <code>tried</code> prune?",
                     "Sides with equal current length. At the start all four are 0, so the first stick is tried on one side only, cutting the search by a factor of 4 immediately."],
                    ["Why check <code>sticks[0] &gt; side</code> up front?",
                     "A stick longer than a side can never be placed. The DFS would find this too, but only after a full failed search."],
                ],
            },
            "Bitmask DP over used sticks": {
                "idea": [
                    "Instead of tracking which side each stick is on, track only <em>which sticks are used</em>. Fill sides one after another: the current side's length is the used total modulo <code>side</code>.",
                    "<code>fill[mask]</code> is that current length if the sticks in <code>mask</code> can be placed this way, or −1 if not.",
                    "A stick can be added to a reachable mask when it fits in the current side; finishing a side wraps the length back to 0.",
                ],
                "steps": [
                    "Reject fewer than 4 sticks or a total not divisible by 4. Set <code>side = total // 4</code>.",
                    "Create <code>fill</code> with 2<sup>n</sup> entries of −1 and set <code>fill[0] = 0</code>.",
                    "Visit masks in increasing order; skip unreachable ones.",
                    "For each unused stick <code>i</code> with <code>fill[mask] + matchsticks[i] &lt;= side</code>, set <code>fill[mask | 1 &lt;&lt; i] = (fill[mask] + matchsticks[i]) % side</code>.",
                    "Return whether <code>fill[-1] == 0</code>: all sticks used, last side exactly closed.",
                ],
                "why": [
                    "The used total of a mask is fixed, so its current-side length is the same however it was reached; one value per mask is enough.",
                    "A mask is reachable exactly when its sticks can be ordered so that no side overflows, which is what a valid square needs.",
                    "Adding a stick only sets bits, so a larger mask is always processed after the masks that reach it. 2<sup>n</sup> masks × n sticks: <strong>O(n · 2<sup>n</sup>)</strong> time.",
                    "The table has 2<sup>n</sup> entries: <strong>O(2<sup>n</sup>)</strong> space.",
                ],
                "dry": [
                    [
                        "side = 2; bits 0–4 are sticks 1, 1, 2, 2, 2 in input order.",
                        "fill[00000] = 0. Single 1s give fill 1; a single 2 closes a side, fill 0.",
                        "Both 1s together (00011) reach 2 → 0. Every mask turns out reachable, with fill = its total mod 2.",
                        "fill[11111] = 8 mod 2 = 0.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "side = 4; bits 0–3 are the 3s, bit 4 is the 4.",
                        "Any single 3 gives fill 3; the 4 alone closes a side, fill 0; the 4 plus one 3 gives fill 3.",
                        "No mask can add a second 3: 3 + 3 = 6 &gt; 4. Only 10 of the 32 masks are reachable.",
                        "fill[11111] stays −1.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can one number per mask stand for the whole state?",
                     "Sides are filled in order and earlier sides are exactly full, so the current side holds the used total minus a multiple of <code>side</code>: the total mod <code>side</code>."],
                    ["Why <code>% side</code> when a side is completed?",
                     "Reaching exactly <code>side</code> means the side is done and the next one starts empty, at 0."],
                    ["When is this better than the DFS?",
                     "When n is up to about 20 and the DFS has bad cases; the DP has a guaranteed bound but always pays 2<sup>n</sup> memory, even when the DFS would finish instantly."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ partition to k equal sum subsets
    "partition-k-equal-subsets": {
        "examples": [
            {"call": "can_partition_k_subsets([4, 3, 2, 3, 5, 2, 1], 4)", "expect": "True"},
            {"call": "can_partition_k_subsets([2, 2, 3, 5], 2)", "expect": "False"},
        ],
        "approaches": {
            "Bucket filling with symmetry pruning": {
                "idea": [
                    "Matchsticks to Square generalised to k sides: put each number into one of k buckets, never letting a bucket pass <code>target = total / k</code>.",
                    "Largest numbers first, so impossible placements fail near the root.",
                    "Buckets holding the same sum are interchangeable, so a number is tried in only one bucket per distinct current sum (the <code>tried</code> set).",
                ],
                "steps": [
                    "If <code>total % k</code> is non-zero, return False. Set <code>target = total // k</code>.",
                    "Sort descending; if the largest exceeds <code>target</code>, return False.",
                    "<code>dfs(i)</code>: if all numbers are placed, return True.",
                    "For each bucket <code>b</code> with room for <code>nums[i]</code> and a sum not yet in <code>tried</code>: record the sum, add the number, recurse, return True on success, else remove it.",
                    "Return False if no bucket works.",
                ],
                "why": [
                    "Buckets never exceed <code>target</code> and the numbers sum to k · target, so a full placement fills every bucket exactly.",
                    "Two buckets with equal sums give identical subproblems, so trying only one of them loses no solution.",
                    "Each number has up to k choices: <strong>O(k<sup>n</sup>)</strong> worst case, much less with the pruning.",
                    "Recursion depth n, plus the k buckets: <strong>O(n + k)</strong> space.",
                ],
                "dry": [
                    [
                        "total 20, k 4, target 5; sorted [5, 4, 3, 3, 2, 2, 1].",
                        "5 → b0. 4 → b1. 3 → b2 (b1 is too full). 3 → b3.",
                        "2 → b2 (b0, b1 too full), making 5. Next 2 → b3, making 5.",
                        "1 → b1, making 5. Buckets [5, 5, 5, 5].",
                        "The result is <strong>True</strong>, without any backtracking.",
                    ],
                    [
                        "total 12, k 2, target 6; sorted [5, 3, 2, 2].",
                        "5 → b0. 3 → b1 (b0 would be 8). 2 → b1, making 5.",
                        "The last 2 fits in neither bucket (both at 5). Undo; b0 is still too full for the 2 and for the 3.",
                        "At the top, 5 in b1 is skipped: sum 0 was already tried.",
                        "The result is <strong>False</strong>: 5 needs a 1 that does not exist.",
                    ],
                ],
                "faq": [
                    ["Why does the <code>tried</code> set matter so much?",
                     "Without it, the first number is tried in all k empty buckets, and every failing state is explored k! times over in its permutations of buckets."],
                    ["Is this the same code as Matchsticks to Square?",
                     "Yes, with 4 replaced by k. The square problem is the case k = 4."],
                    ["What about zeros or negative numbers?",
                     "The problem guarantees positive numbers. Zeros would still work; negatives break the <code>&lt;= target</code> pruning, since a bucket could go over and come back."],
                ],
            },
            "Bitmask DP": {
                "idea": [
                    "Fill buckets one after another. Then the state is just the set of numbers used, and the current bucket holds their total modulo <code>target</code>.",
                    "<code>fill[mask]</code> is that current-bucket sum when the numbers in <code>mask</code> can be placed without overflow, or −1.",
                ],
                "steps": [
                    "Return False if <code>total % k</code> is non-zero; set <code>target</code>.",
                    "Set <code>fill = [-1] * (1 &lt;&lt; n)</code> and <code>fill[0] = 0</code>.",
                    "For each reachable <code>mask</code> in increasing order, and each unused <code>i</code> that fits (<code>fill[mask] + nums[i] &lt;= target</code>):",
                    "set <code>fill[mask | 1 &lt;&lt; i] = (fill[mask] + nums[i]) % target</code>.",
                    "Return <code>fill[-1] == 0</code>.",
                ],
                "why": [
                    "Every mask's sum is fixed, so its current-bucket amount is too; storing one value per mask loses nothing.",
                    "The full mask is reachable exactly when the numbers can be poured into buckets in some order without overflowing, i.e. when a partition exists.",
                    "2<sup>n</sup> masks, n numbers each: <strong>O(n · 2<sup>n</sup>)</strong> time.",
                    "The table is <strong>O(2<sup>n</sup>)</strong> space.",
                ],
                "dry": [
                    [
                        "target 5, n 7: 128 masks over [4, 3, 2, 3, 5, 2, 1].",
                        "fill[0] = 0; adding 5 alone closes a bucket (fill 0); 4 then 1, or 3 then 2, also close one.",
                        "Reachable masks keep fill = their total mod 5; masks like {4, 3} (7 &gt; 5) are never reached.",
                        "The full mask is reached with total 20, fill 0.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "target 6; bits for [2, 2, 3, 5].",
                        "Reachable: {2}, {2}, {2, 2} = 4, {3}, {2, 3} = 5, {5}.",
                        "From 4, adding 3 or 5 overflows; from 5, adding any number overflows.",
                        "Only 8 of 16 masks are reachable, and the full mask is not one of them.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can masks be processed in plain increasing order?",
                     "A transition only adds a bit, producing a larger number, so every mask's predecessors come before it."],
                    ["Is overwriting <code>fill[mask | 1 &lt;&lt; i]</code> safe?",
                     "Yes: every path to the same mask writes the same value, the mask's total mod <code>target</code>."],
                    ["When does this beat the bucket DFS?",
                     "On inputs where the DFS degenerates; it guarantees n · 2<sup>n</sup>, but needs 2<sup>n</sup> memory, so n must stay around 20 or less."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ factor combinations
    "factor-combinations": {
        "examples": [
            {"call": "sorted(get_factors(12))", "expect": "[[2, 2, 3], [2, 6], [3, 4]]"},
            {"call": "get_factors(37)", "expect": "[]"},
        ],
        "approaches": {
            "Factors in non-decreasing order, up to &radic;n": {
                "idea": [
                    "Write each factorisation in non-decreasing order so it is produced once: [2, 6] but never [6, 2].",
                    "At each step pick the next factor <code>f</code> with <code>f * f &lt;= n</code>. Then either stop with the pair <code>f, n // f</code>, or keep splitting <code>n // f</code> with factors at least <code>f</code>.",
                    "Stopping at √n is what keeps the order: if <code>f</code> passed √n, <code>n // f</code> would be smaller than <code>f</code>.",
                ],
                "steps": [
                    "<code>dfs(n, start)</code> tries <code>f</code> from <code>start</code> while <code>f * f &lt;= n</code>.",
                    "If <code>n % f == 0</code>, record <code>path + [f, n // f]</code>: one finished factorisation.",
                    "Then append <code>f</code> to <code>path</code> and call <code>dfs(n // f, f)</code> to split the cofactor further.",
                    "Pop <code>f</code> and continue with <code>f + 1</code>.",
                    "Start with <code>dfs(n, 2)</code>; n itself is never listed alone.",
                ],
                "why": [
                    "Every factorisation into factors ≥ 2, written in non-decreasing order, has a first factor f ≤ √(remaining), so the loop reaches it; recursion with <code>start = f</code> keeps later factors ≥ f.",
                    "The last factor <code>n // f</code> is at least <code>f</code> because <code>f * f &lt;= n</code>, so recorded lists are sorted and therefore unique.",
                    "Each call loops up to √n, and there is one call per prefix of a factorisation: about <strong>O(√n · F)</strong> time for F factorisations.",
                    "A factorisation has at most log₂ n factors, so <code>path</code> and the depth are <strong>O(log n)</strong>.",
                ],
                "dry": [
                    [
                        "dfs(12, 2): f=2 divides: record [2, 6]; recurse dfs(6, 2) with path [2].",
                        "dfs(6, 2): f=2 divides: record [2, 2, 3]; dfs(3, 2) has 2·2 &gt; 3, nothing. f=3: 9 &gt; 6, stop.",
                        "Back in dfs(12, 2): f=3 divides: record [3, 4]; dfs(4, 3) has 9 &gt; 4, nothing.",
                        "f=4: 16 &gt; 12, stop.",
                        "Sorted: <strong>[[2, 2, 3], [2, 6], [3, 4]]</strong>.",
                    ],
                    [
                        "dfs(37, 2): f runs 2..6, since 6 · 6 = 36 ≤ 37 and 7 · 7 &gt; 37.",
                        "None of 2, 3, 4, 5, 6 divides 37.",
                        "Nothing is recorded and no recursion happens.",
                        "37 is prime, so the result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is n itself not in the output?",
                     "Factors must be between 2 and n − 1, so [n] does not count. The loop starts at 2 and every recorded list has at least two factors."],
                    ["Why recurse with <code>start = f</code> rather than 2?",
                     "Allowing smaller factors later would produce [3, 2, 2] as well as [2, 2, 3]."],
                    ["Why record before recursing?",
                     "The pair <code>[f, n // f]</code> is itself an answer; the recursion then finds the ones where <code>n // f</code> is split further."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ brace expansion
    "brace-expansion": {
        "examples": [
            {"call": 'expand("{a,b}c{d,e}f")', "expect": '["acdf", "acef", "bcdf", "bcef"]'},
            {"call": 'expand("{c,a}z")', "expect": '["az", "cz"]'},
        ],
        "approaches": {
            "Parse into option groups, backtrack in sorted order": {
                "idea": [
                    "The string is a sequence of positions, each offering one letter or a braced set of letters. Words are the Cartesian product of those groups.",
                    "Parse first into a list of option lists, sorting each braced set, then build words with the usual choose / explore / un-choose.",
                    "Because each group is sorted and the recursion goes left to right, the words come out sorted.",
                ],
                "steps": [
                    "Scan <code>s</code> with <code>i</code>. On '{', find the matching '}' with <code>s.index</code>, split the inside on ',', sort it, append the group, and jump past it.",
                    "On a plain letter, append the one-option group <code>[s[i]]</code>.",
                    "<code>dfs(g)</code>: if <code>g == len(groups)</code>, join <code>path</code> and record the word.",
                    "Otherwise for each <code>ch</code> in <code>groups[g]</code>: append, recurse on <code>g + 1</code>, pop.",
                    "Call <code>dfs(0)</code> and return <code>out</code>.",
                ],
                "why": [
                    "Every word picks one option per group and every combination is visited once, so the output is exactly the product.",
                    "Sorted groups visited left to right give lexicographic order, the order the problem asks for.",
                    "W words of length L, each joined in O(L): <strong>O(W · L)</strong> time.",
                    "<code>path</code> and the recursion hold at most L items: <strong>O(L)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "Parsed groups: [a, b], [c], [d, e], [f].",
                        "Choose a, c, d, f: record \"acdf\"; swap d for e: \"acef\".",
                        "Back to the first group, choose b: \"bcdf\", \"bcef\".",
                        "Four words in sorted order.",
                        "The result is <strong>[\"acdf\", \"acef\", \"bcdf\", \"bcef\"]</strong>.",
                    ],
                    [
                        "\"{c,a}\" parses to the sorted group [a, c]; then [z].",
                        "Choose a, z: record \"az\".",
                        "Choose c, z: record \"cz\".",
                        "Sorting the group made the output sorted even though c came first in the input.",
                        "The result is <strong>[\"az\", \"cz\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort each group rather than the final list?",
                     "Sorting groups is cheap and makes the depth-first order already lexicographic, so no final sort of W words is needed."],
                    ["Does this handle nested braces?",
                     "No; this problem has none. Nested braces (Brace Expansion II) need a recursive parser that combines sets."],
                    ["What does <code>s.index(\"}\", i)</code> do?",
                     "It finds the first '}' at or after <code>i</code>, which closes the current group because groups never nest."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word pattern II
    "word-pattern-ii": {
        "examples": [
            {"call": 'word_pattern_match("abab", "redblueredblue")', "expect": "True"},
            {"call": 'word_pattern_match("ab", "aa")', "expect": "False"},
        ],
        "approaches": {
            "Backtrack over the length of each new mapping": {
                "idea": [
                    "Walk the pattern letter by letter and the string with a pointer <code>j</code>. A letter seen before is forced: its word must appear at <code>j</code>.",
                    "A new letter can map to any non-empty prefix of what is left, so try each length, recurse, and undo the mapping if it fails.",
                    "The mapping must be a bijection, so a word already claimed by another letter is skipped (<code>claimed</code>).",
                ],
                "steps": [
                    "<code>dfs(i, j)</code>: if the pattern is used up, succeed only if <code>j == len(s)</code>.",
                    "If <code>ch = pattern[i]</code> is in <code>mapping</code>, check <code>s.startswith(w, j)</code> and continue with <code>dfs(i + 1, j + len(w))</code>.",
                    "Otherwise compute <code>last</code>, leaving at least one character for each later pattern letter.",
                    "For each <code>end</code> from <code>j + 1</code> to <code>last</code>, take <code>w = s[j:end]</code>; skip it if claimed; else map and claim it, and return True if <code>dfs(i + 1, end)</code> succeeds.",
                    "On failure delete the mapping and release the word; after the loop return False.",
                ],
                "why": [
                    "Every assignment of words to letters that could match is tried, and forced letters are checked exactly, so a matching bijection is found if one exists.",
                    "Undoing <code>mapping</code> and <code>claimed</code> on failure restores the state for the next length, so branches do not leak into each other.",
                    "With p pattern letters and n characters, up to n lengths per new letter: <strong>O(n<sup>p</sup>)</strong> in the worst case.",
                    "The recursion is p deep and the maps hold at most p words: <strong>O(p)</strong> space (plus the word strings).",
                ],
                "dry": [
                    [
                        "a → \"r\". b tries \"e\", \"ed\", \"edb\", \"edbl\", \"edblu\": each time the forced a needs \"r\" at the next position and finds another letter.",
                        "b → \"edblue\" (end 7): forced a finds \"r\" at index 7.",
                        "Forced b finds \"edblue\" at index 8, ending at 14 = len(s).",
                        "The search accepts a = \"r\", b = \"edblue\" before ever trying a = \"red\": r·edblue·r·edblue spells the string too.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "a: last = 2 − 1 = 1, so a can only be \"a\" (end 1). Map it and claim \"a\".",
                        "b: last = 2, so b can only be s[1:2] = \"a\".",
                        "\"a\" is already claimed by a, so it is skipped; b has no options.",
                        "a has no other length either.",
                        "The result is <strong>False</strong>: two letters cannot share a word.",
                    ],
                ],
                "faq": [
                    ["Why is <code>claimed</code> needed when <code>mapping</code> exists?",
                     "<code>mapping</code> stops one letter having two words; <code>claimed</code> stops two letters having one word. Without it, \"ab\" would match \"aa\"."],
                    ["What does <code>last</code> buy?",
                     "Each later letter needs at least one character, so a new word may not use them up. It cuts lengths that are bound to fail."],
                    ["Why did it find a = \"r\" rather than a = \"red\"?",
                     "Shorter words are tried first and any bijection that spells the string is a valid answer. The question is only whether one exists."],
                ],
            },
        },
    },


    # ------------------------------------------------------------------ android unlock patterns
    "android-unlock-patterns": {
        "examples": [
            {"call": "number_of_patterns(1, 2)", "expect": "65"},
            {"call": "number_of_patterns(3, 2)", "expect": "0"},
        ],
        "approaches": {
            "Backtracking with a skip table and symmetry": {
                "idea": [
                    "Count patterns by DFS over keys: from the current key, any unvisited key can follow, unless the move jumps over a key that has not been visited yet.",
                    "<code>skip[a][b]</code> names the key lying between a and b (for example 2 between 1 and 3), or 0 if the move jumps over nothing.",
                    "The keypad is symmetric: the four corners give the same counts, as do the four edges, so count from 1, 2 and 5 only and multiply.",
                ],
                "steps": [
                    "Fill <code>skip</code> for the 8 lines through a middle key, in both directions.",
                    "<code>dfs(cur, length)</code>: <code>count</code> starts at 1 if <code>length &gt;= m</code> (the pattern ending here counts), else 0.",
                    "If <code>length == n</code>, return <code>count</code>: no longer pattern is allowed.",
                    "Mark <code>cur</code> visited; for each <code>nxt</code> that is unvisited and whose <code>mid</code> is 0 or visited, add <code>dfs(nxt, length + 1)</code>.",
                    "Unmark <code>cur</code> and return <code>count</code>. The answer is <code>4 * dfs(1, 1) + 4 * dfs(2, 1) + dfs(5, 1)</code>.",
                ],
                "why": [
                    "Each pattern is one path of distinct keys obeying the jump rule, and the DFS enumerates such paths; each is counted at its end if its length is in [m, n].",
                    "Rotating or reflecting the keypad maps corners to corners and edges to edges while preserving the jump rule, so their counts are equal.",
                    "At most 9! orderings of keys exist: <strong>O(9!)</strong> time, constant in the input, and symmetry does about a third of the work.",
                    "<code>visited</code>, <code>skip</code> and a recursion depth of at most 9: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "dfs(1, 1): count 1. Next keys: 2, 4, 5, 6, 8 are legal; 3, 7, 9 jump over unvisited 2, 4, 5. Each returns 1 at length 2. Total 6.",
                        "dfs(2, 1): count 1. Every key except 8 (jumps over 5) is legal: 7 more. Total 8.",
                        "dfs(5, 1): count 1, and all 8 others are adjacent or diagonal. Total 9.",
                        "4 · 6 + 4 · 8 + 9 = 24 + 32 + 9.",
                        "The result is <strong>65</strong>.",
                    ],
                    [
                        "m = 3 is larger than n = 2.",
                        "Every call at length 1 or 2 starts with count 0, since length &lt; m.",
                        "Recursion stops at length 2, so no pattern is ever long enough.",
                        "The result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why may a move pass over a key that is already visited?",
                     "That is the Android rule: a line through a visited dot is fine, which is why the check is <code>mid == 0 or visited[mid]</code>."],
                    ["Why mark <code>cur</code> after the length checks?",
                     "When <code>length == n</code> the function returns without exploring, so no marking is needed; marking happens only around the loop that uses it."],
                    ["Is the symmetry needed?",
                     "No, the all-nine version gives the same count. Symmetry cuts the work from 9 starts to 3."],
                ],
            },
            "Backtracking from all nine keys": {
                "idea": [
                    "The same DFS with the same skip table, but started from every key and summed.",
                    "Simpler to trust: it does not rely on the symmetry argument.",
                ],
                "steps": [
                    "Build <code>skip</code> for the 8 lines with a middle key.",
                    "<code>dfs(cur, length)</code> counts this pattern when <code>length &gt;= m</code>, returns at <code>length == n</code>.",
                    "Otherwise mark <code>cur</code>, add <code>dfs(nxt, length + 1)</code> for each legal <code>nxt</code>, unmark.",
                    "Return <code>sum(dfs(k, 1) for k in range(1, 10))</code>.",
                ],
                "why": [
                    "Every pattern starts at some key, and the DFS from that key counts it once.",
                    "The skip check enforces the only geometric rule; distinctness comes from <code>visited</code>.",
                    "At most 9! paths: <strong>O(9!)</strong> time, about three times the symmetric version.",
                    "<strong>O(1)</strong> space: fixed-size tables and depth at most 9.",
                ],
                "dry": [
                    [
                        "Corner keys 1, 3, 7, 9 each return 1 + 5 = 6.",
                        "Edge keys 2, 4, 6, 8 each return 1 + 7 = 8.",
                        "Centre key 5 returns 1 + 8 = 9.",
                        "6 · 4 + 8 · 4 + 9 = 65.",
                        "The result is <strong>65</strong>.",
                    ],
                    [
                        "Each of the nine starts runs with m = 3, n = 2.",
                        "Length never reaches 3, so no call counts itself.",
                        "Every start returns 0.",
                        "The result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>skip</code> filled in both directions?",
                     "Moving 3 → 1 crosses 2 just like 1 → 3, so <code>skip[a][b] = skip[b][a] = mid</code>."],
                    ["Why do 1 → 6 and 1 → 8 count as legal?",
                     "Those moves are knight-like and pass between dots without crossing one, so <code>skip</code> is 0."],
                    ["Would memoisation help?",
                     "A memo over (visited mask, current key) has 2<sup>9</sup> · 9 states and would speed it up, but 9! is already small."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ N-Queens
    "n-queens": {
        "examples": [
            {"call": "sorted(solve_n_queens(4))",
             "expect": '[["..Q.", "Q...", "...Q", ".Q.."], [".Q..", "...Q", "Q...", "..Q."]]'},
            {"call": "solve_n_queens(3)", "expect": "[]"},
        ],
        "approaches": {
            "One row at a time, three sets of attacked lines": {
                "idea": [
                    "Every row holds exactly one queen, so place them row by row and choose only the column.",
                    "A square (r, c) is attacked through its column <code>c</code>, its diagonal <code>r - c</code> and its anti-diagonal <code>r + c</code>. Three sets make the safety check O(1).",
                    "Place a queen, recurse to the next row, then remove it from all three sets: choose, explore, un-choose.",
                ],
                "steps": [
                    "<code>dfs(r)</code>: if <code>r == n</code>, every row has a queen; build the board strings from <code>place</code> and record them.",
                    "For each column <code>c</code>, skip it if <code>c in cols</code>, <code>r - c in diag</code> or <code>r + c in anti</code>.",
                    "Otherwise add <code>c</code>, <code>r - c</code> and <code>r + c</code> to the sets and append <code>c</code> to <code>place</code>.",
                    "Recurse with <code>dfs(r + 1)</code>.",
                    "Remove the three entries and pop <code>place</code>. Start with <code>dfs(0)</code>.",
                ],
                "why": [
                    "Squares on one diagonal share <code>r - c</code> and squares on one anti-diagonal share <code>r + c</code>, so the sets catch every attack; rows cannot clash by construction.",
                    "Every safe placement is reached because every column is tried in every row.",
                    "Row r has at most n − r free columns, so the tree has at most n! leaves: <strong>O(n!)</strong> time (building each board adds O(n²) per solution).",
                    "Three sets, <code>place</code> and the recursion are all O(n): <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "Row 0, c=0: row 1 can only take c=2 (dead: row 2 all blocked) or c=3, then row 2 c=1, then row 3 is fully blocked.",
                        "Row 0, c=1: row 1 c=3, row 2 c=0, row 3 c=2: solution [1, 3, 0, 2].",
                        "Row 0, c=2: row 1 c=0, row 2 c=3, row 3 c=1: solution [2, 0, 3, 1].",
                        "Row 0, c=3: row 1 c=0 and c=1 both dead-end at rows 2–3.",
                        "Boards [\".Q..\", \"...Q\", \"Q...\", \"..Q.\"] and [\"..Q.\", \"Q...\", \"...Q\", \".Q..\"]; sorted: <strong>[[\"..Q.\", \"Q...\", \"...Q\", \".Q..\"], [\".Q..\", \"...Q\", \"Q...\", \"..Q.\"]]</strong>.",
                    ],
                    [
                        "Row 0, c=0: row 1 c=0 is the same column, c=1 is the same diagonal (r − c = 0); c=2 is placed. Row 2: c=0, c=2 columns used, c=1 anti-diagonal 3 used.",
                        "Row 0, c=1: row 1 has c=0 on anti-diagonal 1, c=1 in the column, c=2 on diagonal −1: all blocked.",
                        "Row 0, c=2: row 1 c=0 placed, then row 2 is fully blocked; c=1, c=2 in row 1 are blocked.",
                        "No branch ever reaches r = 3.",
                        "The result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>r - c</code> for one diagonal and <code>r + c</code> for the other?",
                     "Moving down-right adds 1 to both r and c, so r − c is constant; moving down-left adds 1 to r and subtracts 1 from c, so r + c is constant."],
                    ["Why is no row set needed?",
                     "Each call places exactly one queen in row <code>r</code> and moves on, so two queens can never share a row."],
                    ["Why build board strings only at the end?",
                     "Keeping just the column per row is cheaper to update; the strings are needed only for complete solutions."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ N-Queens II
    "n-queens-ii": {
        "examples": [
            {"call": "total_n_queens(4)", "expect": "2"},
            {"call": "total_n_queens(3)", "expect": "0"},
        ],
        "approaches": {
            "Bitmask backtracking": {
                "idea": [
                    "Only the count is needed, so the attacked columns can be three n-bit integers instead of sets: <code>cols</code>, <code>d1</code> and <code>d2</code>, all seen from the current row.",
                    "The free squares in the row are <code>full &amp; ~(cols | d1 | d2)</code>, and <code>free &amp; -free</code> picks them off one bit at a time.",
                    "Going to the next row, one diagonal mask shifts left and the other right, because a diagonal moves one column per row.",
                ],
                "steps": [
                    "<code>full</code> has the low n bits set. <code>dfs(cols, d1, d2)</code>: if <code>cols == full</code>, every column has a queen: return 1.",
                    "Compute <code>free = full &amp; ~(cols | d1 | d2)</code>.",
                    "While <code>free</code> is non-zero, take the lowest bit <code>bit = free &amp; -free</code> and clear it with <code>free ^= bit</code>.",
                    "Add <code>dfs(cols | bit, (d1 | bit) &lt;&lt; 1 &amp; full, (d2 | bit) &gt;&gt; 1)</code>.",
                    "Return the total. Start with <code>dfs(0, 0, 0)</code>.",
                ],
                "why": [
                    "A queen attacks its column in every later row, and along its two diagonals one more column to the left or right per row: exactly what the shifts track.",
                    "<code>cols == full</code> happens only after n queens, one per row, none attacking another.",
                    "The search tree is the same as the set version: <strong>O(n!)</strong> time, but each step is a few machine-word operations.",
                    "Three integers per frame and depth n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "full = 1111. Row 0 frees all four columns.",
                        "Bit 0001: row 1 free 1100. Bit 0100 leaves row 2 with free 0000. Bit 1000 leads to row 2 free 0010, then row 3 free 0000: dead.",
                        "Bit 0010: row 1 free 1000 → row 2 free 0001 → row 3 free 0100 → cols = 1111, count 1.",
                        "Bit 0100 mirrors it: 0001 → 1000 → 0010, count 1. Bit 1000 dead-ends.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "full = 111. Row 0: free 111.",
                        "Bit 001: row 1 free 100 → row 2 free 000. Bit 010: row 1 free 000.",
                        "Bit 100: row 1 free 001 → row 2 free 000.",
                        "<code>cols</code> never becomes 111.",
                        "The result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&amp; full</code> after the left shift but not after the right shift?",
                     "A left shift can push a bit above position n − 1, which must be cut off. A right shift just drops bits off the low end."],
                    ["How does <code>free &amp; -free</code> isolate the lowest bit?",
                     "In two's complement, <code>-free</code> flips every bit above the lowest set bit, so AND keeps only that bit."],
                    ["Why is <code>cols == full</code> the base case rather than a row counter?",
                     "Each level adds exactly one column bit, so all n bits set means n queens have been placed."],
                ],
            },
            "Sets of attacked lines": {
                "idea": [
                    "The N-Queens search, returning a count instead of boards.",
                    "Each row tries every column not attacked through <code>cols</code>, <code>diag</code> (r − c) or <code>anti</code> (r + c).",
                ],
                "steps": [
                    "<code>dfs(r)</code>: if <code>r == n</code>, return 1.",
                    "Set <code>count = 0</code> and loop over columns <code>c</code>.",
                    "Skip <code>c</code> if any of the three sets contains its line.",
                    "Otherwise add the three entries, add <code>dfs(r + 1)</code> to <code>count</code>, and remove them.",
                    "Return <code>count</code>; the answer is <code>dfs(0)</code>.",
                ],
                "why": [
                    "Same correctness argument as N-Queens: each safe placement of one queen per row is one leaf, counted once.",
                    "<strong>O(n!)</strong> time, with set operations instead of bit tricks.",
                    "Three sets of at most n entries and depth n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Row 0, c=0: dead at row 2 or 3.",
                        "Row 0, c=1 → 3 → 0 → 2 reaches r = 4: returns 1.",
                        "Row 0, c=2 → 0 → 3 → 1: returns 1.",
                        "Row 0, c=3: dead.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "Row 0, c=0 → row 1 c=2 → row 2 blocked.",
                        "Row 0, c=1: row 1 blocked everywhere.",
                        "Row 0, c=2 → row 1 c=0 → row 2 blocked.",
                        "The result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Which is faster, sets or bitmasks?",
                     "Same tree, but bitmasks avoid hashing and the column loop, so they are several times faster in practice."],
                    ["Can symmetry halve the work?",
                     "Yes: count solutions with the first queen in the left half and double, handling the middle column separately when n is odd."],
                    ["Why return counts instead of using a global counter?",
                     "Returning sums keeps the function pure and avoids <code>nonlocal</code>; both work."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word break II
    "word-break-ii": {
        "examples": [
            {"call": 'sorted(word_break("catsanddog", ["cat", "cats", "and", "sand", "dog"]))',
             "expect": '["cat sand dog", "cats and dog"]'},
            {"call": 'word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])', "expect": "[]"},
        ],
        "approaches": {
            "Memoised sentences per suffix": {
                "idea": [
                    "Every sentence for <code>s[i:]</code> is a dictionary word <code>s[i:j]</code> followed by a sentence for <code>s[j:]</code>.",
                    "Suffixes repeat across branches, so cache <code>sentences(i)</code>: each suffix's list is built once.",
                    "Words longer than <code>longest</code> cannot match, which bounds the inner loop.",
                ],
                "steps": [
                    "Put the words in a set and compute <code>longest</code>.",
                    "<code>sentences(i)</code>: if <code>i == len(s)</code>, return <code>[\"\"]</code>, one empty sentence.",
                    "For each <code>j</code> from <code>i + 1</code> to <code>min(len(s), i + longest)</code>, if <code>w = s[i:j]</code> is a word, extend every <code>rest</code> in <code>sentences(j)</code>.",
                    "Join as <code>w + \" \" + rest</code>, or just <code>w</code> when <code>rest</code> is empty.",
                    "Return <code>sentences(0)</code>.",
                ],
                "why": [
                    "By induction on the suffix length, <code>sentences(i)</code> holds exactly the segmentations of <code>s[i:]</code>.",
                    "A suffix with no segmentation returns [], and every caller then adds nothing, so dead suffixes are explored only once.",
                    "There are n suffixes with up to n candidate words each, plus the cost of building the output: <strong>O(n² + output)</strong> time.",
                    "The cache stores the sentence lists of every suffix: <strong>O(n · output)</strong> space in the worst case.",
                ],
                "dry": [
                    [
                        "sentences(0) tries \"cat\" → sentences(3) and \"cats\" → sentences(4).",
                        "sentences(3): \"sand\" → sentences(7): \"dog\" → sentences(10) = [\"\"], so sentences(7) = [\"dog\"] and sentences(3) = [\"sand dog\"].",
                        "sentences(4): \"and\" → sentences(7), served from the cache: [\"and dog\"].",
                        "sentences(0) = [\"cat sand dog\", \"cats and dog\"].",
                        "Sorted: <strong>[\"cat sand dog\", \"cats and dog\"]</strong>.",
                    ],
                    [
                        "sentences(0) tries \"cat\" → 3 and \"cats\" → 4.",
                        "sentences(3): \"sand\" → sentences(7) on \"og\": no word, so [].",
                        "sentences(4): \"and\" → sentences(7), cached as []. Both are [].",
                        "sentences(0) finds no complete sentence.",
                        "The result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the base case return <code>[\"\"]</code> and not []?",
                     "[] would mean the end of the string cannot be segmented, so no sentence would ever form. [\"\"] means one way: the empty sentence."],
                    ["What does <code>longest</code> save?",
                     "Without it each <code>i</code> slices up to n substrings. With it, only up to <code>longest</code>, the longest dictionary word."],
                    ["Can the output itself be exponential?",
                     "Yes: \"aaaaaaaaaa\" with [\"a\", \"aa\"] has 89 sentences. No method avoids writing them all; memoisation just avoids redoing dead suffixes."],
                ],
            },
            "Backtracking pruned by a word-break table": {
                "idea": [
                    "Plain backtracking can waste exponential time on suffixes that cannot be segmented at all, like \"aaaa…ab\".",
                    "First compute <code>ok[i]</code>: can <code>s[i:]</code> be segmented? That is Word Break I, a right-to-left DP.",
                    "Then backtrack, but only cut at <code>j</code> where <code>ok[j]</code> is True, so every branch taken leads to at least one sentence.",
                ],
                "steps": [
                    "Set <code>ok[n] = True</code>; for <code>i</code> from n − 1 down, <code>ok[i]</code> is True if some <code>s[i:j]</code> is a word and <code>ok[j]</code>.",
                    "If <code>ok[0]</code> is False, return [] without searching.",
                    "<code>dfs(i)</code>: if <code>i == n</code>, join <code>path</code> with spaces and record it.",
                    "For each <code>j</code> with <code>ok[j]</code> and <code>s[i:j]</code> in the word set: append the word, recurse on <code>j</code>, pop.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "<code>ok[j]</code> guarantees the rest can be finished, so the search never enters a dead branch and its work is proportional to the output.",
                    "The table costs <strong>O(n²)</strong> slices; the search adds O(n) per recorded sentence for slicing and joining: <strong>O(n² + output · n)</strong> time.",
                    "<code>ok</code>, <code>path</code> and the recursion: <strong>O(n)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "ok is True at 10, 7 (\"dog\"), 4 (\"and\"), 3 (\"sand\") and 0.",
                        "dfs(0): \"cat\" (ok[3]) → \"sand\" (ok[7]) → \"dog\" → record \"cat sand dog\".",
                        "dfs(0): \"cats\" (ok[4]) → \"and\" → \"dog\" → record \"cats and dog\".",
                        "No other cut is ever tried that fails later.",
                        "The result is <strong>[\"cat sand dog\", \"cats and dog\"]</strong>.",
                    ],
                    [
                        "ok is True only at 9 and 6 (\"dog\"): positions 3 and 4 cannot reach the end because \"og\" is not a word.",
                        "So ok[0] is False.",
                        "The search is never started.",
                        "The result is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not skip the table and just backtrack?",
                     "On \"a\" * 40 + \"b\" with [\"a\", \"aa\", \"aaa\"], every prefix splits many ways and none can finish; plain backtracking explores an exponential number of them before returning []."],
                    ["Why check <code>ok[j]</code> before the dictionary test?",
                     "Both are needed; testing the cheap boolean first skips a slice and hash for most <code>j</code>."],
                    ["How does this compare with the memoised version?",
                     "Same results. This one stores only booleans, not lists of sentences per suffix, so it uses less memory."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ robot room cleaner
    "robot-room-cleaner": {
        "examples": [
            {"setup": ROBOT_1, "call": "sorted(robot.cleaned)",
             "expect": "[(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)]"},
            {"setup": ROBOT_2, "call": "sorted(robot.cleaned)", "expect": "[(0, 0), (0, 1), (0, 2)]"},
        ],
        "approaches": {
            "DFS in the robot's own coordinates, physically backtracking": {
                "idea": [
                    "The robot knows neither the map nor its position, so invent coordinates: call the start (0, 0) and the starting heading \"up\". Every cell is then named relative to the start.",
                    "Do an ordinary DFS over cells, using <code>visited</code> in these private coordinates. <code>move()</code> doubles as the wall test.",
                    "Backtracking is physical: after exploring a neighbour the robot must actually drive back and face the same way, which <code>go_back</code> does with two turns, a move and two turns.",
                ],
                "steps": [
                    "<code>dfs(cell, d)</code>: add <code>cell</code> to <code>visited</code> and call <code>robot.clean()</code>. The robot is at <code>cell</code> facing <code>d</code>.",
                    "For <code>k</code> in 0..3, the heading is <code>nd = (d + k) % 4</code> and the neighbour is <code>nxt</code>.",
                    "If <code>nxt</code> is unvisited and <code>robot.move()</code> succeeds, call <code>dfs(nxt, nd)</code>, then <code>go_back()</code> to return to <code>cell</code> facing <code>nd</code>.",
                    "Either way, <code>robot.turnRight()</code> to face the next direction clockwise.",
                    "After four right turns the robot faces <code>d</code> again, which the caller's <code>go_back</code> relies on. Start with <code>dfs((0, 0), 0)</code>.",
                ],
                "why": [
                    "Every reachable cell is adjacent to some visited cell, and each visited cell tries all four directions, so DFS reaches them all.",
                    "The invariant \"when <code>dfs(cell, d)</code> returns, the robot is at <code>cell</code> facing <code>d</code>\" holds by induction: each branch is undone by <code>go_back</code>, and the four turns cancel.",
                    "Each of the N open cells is entered once and tries 4 directions with O(1) robot calls: <strong>O(N)</strong> time.",
                    "<code>visited</code> holds N cells and the recursion can be N deep: <strong>O(N)</strong> space.",
                ],
                "dry": [
                    [
                        "Real start (1,0) is private (0,0), facing up. Clean it. Up moves to real (0,0), private (−1,0): clean.",
                        "From there: up hits the edge; right moves to real (0,1): clean. Its right is a wall, down moves to real (1,1): clean.",
                        "At real (1,1) facing down: down is the edge, left and up are visited (no move); right moves to real (1,2): clean. All its other moves fail or are visited.",
                        "<code>go_back</code> three times returns the robot along the path to real (0,0), then once more to real (1,0); remaining directions there are visited or blocked.",
                        "Cleaned, sorted: <strong>[(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)]</strong>.",
                    ],
                    [
                        "Real start (0,1), facing up. Clean it. Up is the edge: <code>move()</code> fails.",
                        "Right moves to real (0,2): clean. There, right and down fail, left is visited, up fails. <code>go_back</code> returns to (0,1).",
                        "Down fails. Left moves to real (0,0): clean; its moves fail or are visited; <code>go_back</code>.",
                        "Four turns at the start leave the robot facing up again.",
                        "Cleaned, sorted: <strong>[(0, 0), (0, 1), (0, 2)]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the robot's true heading irrelevant?",
                     "Only relative turns matter. Calling the start heading \"up\" just rotates the private map; every cell still gets a unique name."],
                    ["Why skip <code>move()</code> for visited cells?",
                     "Moving into a visited cell would waste the move and then need a <code>go_back</code>. Checking <code>visited</code> first avoids both."],
                    ["Why <code>turnRight()</code> even when the move succeeded?",
                     "<code>go_back</code> leaves the robot facing <code>nd</code>, the same as before the move, so one right turn always advances to the next direction."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ word search II
    "word-search-ii": {
        "examples": [
            {"setup": WS_BOARD, "call": 'sorted(find_words([row[:] for row in board], ["oath", "pea", "eat", "rain"]))',
             "expect": '["eat", "oath"]'},
            {"call": 'sorted(find_words([["a", "a"]], ["a", "aa", "aaa"]))', "expect": '["a", "aa"]'},
        ],
        "approaches": {
            "Trie-guided DFS, pruning found words": {
                "idea": [
                    "Searching for each word separately repeats work for shared prefixes. Put all words in a trie and walk the board and the trie together, so one DFS looks for every word at once.",
                    "A path is extended only while its letters are a prefix of some word, i.e. while the trie has a matching child.",
                    "Found words are removed from the trie, and empty trie branches are deleted, so later searches skip them entirely.",
                ],
                "steps": [
                    "Build the trie; the end node of each word stores it under <code>\"$\"</code>.",
                    "Start <code>dfs(r, c, trie)</code> from every cell whose letter is a child of the root.",
                    "In <code>dfs</code>, let <code>node = parent[ch]</code>. If it has <code>\"$\"</code>, pop that word into <code>out</code>.",
                    "Mark the cell <code>\"#\"</code> and recurse into each in-bounds neighbour whose letter is a child of <code>node</code>; then restore the letter.",
                    "If <code>node</code> is now empty, delete it from <code>parent</code>: nothing below it remains to be found.",
                ],
                "why": [
                    "Every board path spelling a word is a path in the trie, so the DFS that follows the trie finds every word that exists.",
                    "Popping <code>\"$\"</code> reports each word once even if it appears in several places.",
                    "Each start branches at most 3 ways per letter up to the longest word length L: <strong>O(R · C · 3<sup>L</sup>)</strong> time, with pruning usually doing far better.",
                    "The trie stores all letters of all words: <strong>O(total word length)</strong> space, plus O(L) recursion.",
                ],
                "dry": [
                    [
                        "The trie has branches o-a-t-h, p-e-a, e-a-t, r-a-i-n.",
                        "(0,0) 'o' → (0,1) 'a' → (1,1) 't' → (2,1) 'h': found \"oath\". Its branch empties, so h, t, a and o are deleted on the way back.",
                        "(1,0) 'e' has no neighbour 'a'. (1,3) 'e' → (1,2) 'a' → (1,1) 't': found \"eat\"; the e-branch is deleted.",
                        "(2,3) 'r' has no neighbour 'a'. No 'p' exists on the board.",
                        "Sorted: <strong>[\"eat\", \"oath\"]</strong>.",
                    ],
                    [
                        "The trie is a single chain a → a → a, with \"a\", \"aa\" and \"aaa\" stored along it.",
                        "Start (0,0): found \"a\". Neighbour (0,1) is 'a': found \"aa\". From there (0,0) is '#', so \"aaa\" cannot continue.",
                        "Start (0,1): \"a\" and \"aa\" were already popped, so nothing new; (0,0) leads nowhere.",
                        "\"aaa\" stays in the trie: the board has only two cells.",
                        "Sorted: <strong>[\"a\", \"aa\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why pop <code>\"$\"</code> instead of reading it?",
                     "A word can be spelled by several paths. Popping guarantees it is added to <code>out</code> only once."],
                    ["Why delete empty trie nodes?",
                     "Once every word below a node is found, walking into it again is wasted. Deleting it prunes those paths for all later starts."],
                    ["Why check <code>board[nr][nc] in node</code> before recursing?",
                     "It prunes before the call and also rejects '#' cells, since '#' is never a trie key."],
                ],
            },
            "Word Search once per word": {
                "idea": [
                    "Reuse the Word Search DFS and run it for each distinct word.",
                    "Easy to write and obviously correct, but the board is searched again for every word, even when many words share a prefix.",
                ],
                "steps": [
                    "Deduplicate the word list with <code>dict.fromkeys</code>, keeping the order.",
                    "<code>exist(word)</code> runs <code>dfs(r, c, 0)</code> from every cell.",
                    "<code>dfs</code> fails on a mismatch, succeeds at the last letter, otherwise marks the cell, tries the four neighbours, and restores it.",
                    "Keep the words for which <code>exist</code> is True.",
                ],
                "why": [
                    "Each word's search is the exact Word Search algorithm, so a word is kept precisely when it can be traced on the board.",
                    "W words, each costing up to R · C · 3<sup>L</sup>: <strong>O(W · R · C · 3<sup>L</sup>)</strong> time.",
                    "Only one search is active at a time: <strong>O(L)</strong> recursion space.",
                    "It shows the cost the trie avoids: shared prefixes like \"oa\" are explored once per word here.",
                ],
                "dry": [
                    [
                        "\"oath\": from (0,0) o → a(0,1) → t(1,1) → h(2,1): True.",
                        "\"pea\": no cell holds 'p', so every start fails at once: False.",
                        "\"eat\": from (1,3) e → a(1,2) → t(1,1): True. \"rain\": (2,3) 'r' has no neighbour 'a': False.",
                        "Kept in input order: [\"oath\", \"eat\"].",
                        "Sorted: <strong>[\"eat\", \"oath\"]</strong>.",
                    ],
                    [
                        "\"a\": (0,0) matches the last letter at once: True.",
                        "\"aa\": (0,0) → (0,1): True.",
                        "\"aaa\": (0,0) → (0,1) → (0,0) is '#'; starting at (0,1) fails the same way: False.",
                        "Sorted: <strong>[\"a\", \"aa\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>dict.fromkeys(words)</code>?",
                     "It removes duplicate words while keeping their order, so a repeated word is neither searched twice nor reported twice."],
                    ["When is this acceptable?",
                     "For a handful of words or a tiny board. With thousands of words, the trie version is the expected answer."],
                    ["Is the board restored between words?",
                     "Yes: each <code>dfs</code> puts its letter back before returning, so the next word sees the original board."],
                ],
            },
        },
    },
}
