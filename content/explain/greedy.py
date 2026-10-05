"""Write-ups for the Greedy topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ lemonade change
    "lemonade-change": {
        "example": {"call": "lemonade_change([5, 5, 10, 20, 5, 5, 5, 20])", "expect": "True"},
        "approaches": {
            "Try both ways of making change (search)": {
                "idea": [
                    "The only real decision is how to break a $20: with $10 + $5, or with three $5s.",
                    "Without any insight, try both options whenever both are possible, and succeed if either leads to serving everyone.",
                    "The state is (customer index, number of $5s, number of $10s), and caching it avoids repeated work.",
                ],
                "steps": [
                    "<code>ok(i, fives, tens)</code>: past the last customer means success.",
                    "A $5 adds a five; a $10 needs a five back.",
                    "A $20 tries $10 + $5 first, then three $5s.",
                ],
                "why": [
                    "It explores every way of making change, so it cannot miss a valid one.",
                    "It is exponential without the cache. This is the search the greedy argument makes unnecessary.",
                ],
                "dry": [
                    "5, 5: two fives. 10: give back one five, leaving 1 five and 1 ten.",
                    "20: both ways? Only $10 + $5 is possible (there are not three fives), leaving 0 and 0.",
                    "5, 5, 5: three fives. 20: no ten, so the first branch fails; three fives works.",
                    "All customers are served, so the result is <strong>True</strong>.",
                ],
            },
            "Count bills, prefer giving a $10": {
                "idea": [
                    "A $5 can make change for both $10 and $20 payments; a $10 only helps with $20s. So $5s are the more valuable bill to keep.",
                    "When a $20 arrives, hand back $10 + $5 if possible and keep the fives; only fall back to three $5s.",
                    "Paying with the $10 always leaves at least as many fives as the alternative, so it can never hurt later.",
                ],
                "steps": [
                    "Track <code>fives</code> and <code>tens</code> ($20s are never given as change).",
                    "$5: one more five. $10: needs a five back, or fail.",
                    "$20: use a ten and a five if both are there, otherwise three fives, otherwise fail.",
                ],
                "why": [
                    "This is an exchange argument: any successful plan that uses three fives can swap in ten + five and still succeed.",
                    "One pass and two counters: O(n) time, O(1) space.",
                ],
                "dry": [
                    "5, 5: fives = 2. 10: fives = 1, tens = 1.",
                    "20: a ten and a five are available, so fives = 0 and tens = 0.",
                    "5, 5, 5: fives = 3.",
                    "20: no ten, but fives ≥ 3, so fives = 0.",
                    "Everyone is served: <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max circular subarray
    "max-circular-subarray": {
        "example": {"call": "max_subarray_sum_circular([3, -1, -6, 4, 2])", "expect": "9"},
        "approaches": {
            "Every start, every length": {
                "idea": [
                    "On a circle, a subarray is a start index plus a length of up to n, wrapping past the end.",
                    "Try every start, extend around the circle with a running sum, and keep the best total.",
                ],
                "steps": [
                    "For each start i, add <code>nums[(i + k) % n]</code> for k = 0..n-1.",
                    "Update <code>best</code> after each addition.",
                ],
                "why": [
                    "Every circular subarray is examined.",
                    "It is O(n²) time and O(1) space.",
                ],
                "dry": [
                    "Start 0 gives running sums 3, 2, -4, 0, 2.",
                    "Start 3 gives 4, 6, then wraps: 6 + 3 = <strong>9</strong>, then 8, then 2.",
                    "No other start beats 9, so the result is <strong>9</strong>, the wrapping subarray [4, 2, 3].",
                ],
            },
            "Best prefix plus best suffix": {
                "idea": [
                    "A subarray either does not wrap (ordinary Kadane finds the best one) or wraps around.",
                    "A wrapping subarray is a suffix of the array followed by a prefix, and the two do not overlap.",
                    "Precompute the best prefix sum ending at or before each index, then pair every suffix with the best prefix before it.",
                ],
                "steps": [
                    "Run Kadane for the non-wrapping best.",
                    "<code>right_max[i]</code> = the best prefix sum within <code>nums[:i+1]</code>.",
                    "For each suffix start j, try <code>suffix_sum + right_max[j - 1]</code>.",
                ],
                "why": [
                    "Every wrapping subarray is some suffix plus the best prefix that does not overlap it.",
                    "It is three linear passes: O(n) time and O(n) space.",
                ],
                "dry": [
                    "Kadane, non-wrapping: the best is 4 + 2 = 6.",
                    "Prefix sums are 3, 2, -4, 0, 2, so right_max = [3, 3, 3, 3, 3].",
                    "Suffix [2] + 3 = 5. Suffix [4, 2] + right_max[2] = 6 + 3 = <strong>9</strong>.",
                    "The longer suffixes give 0 + 3 and -1 + 3.",
                    "The best overall is <strong>9</strong>.",
                ],
            },
            "Kadane for max and min together": {
                "idea": [
                    "A wrapping subarray is everything <em>except</em> a non-wrapping middle piece.",
                    "To make the wrapping part as large as possible, leave out the piece with the <em>smallest</em> sum: the answer is <code>total - min subarray</code>.",
                    "Run Kadane for the maximum and for the minimum in the same pass. If every number is negative, the wrap would leave out everything, so return the plain maximum.",
                ],
                "steps": [
                    "Keep <code>total</code>, <code>cur_max</code> / <code>best</code> and <code>cur_min</code> / <code>worst</code>.",
                    "<code>cur_max = max(x, cur_max + x)</code>; <code>cur_min = min(x, cur_min + x)</code>.",
                    "Return <code>best</code> if it is negative, otherwise <code>max(best, total - worst)</code>.",
                ],
                "why": [
                    "Both Kadane runs are the standard maximum-subarray argument, one of them mirrored.",
                    "It is one pass: O(n) time, O(1) space.",
                ],
                "dry": [
                    "The total is 3 - 1 - 6 + 4 + 2 = 2.",
                    "The max Kadane run gives 3, 2, -4, 4, 6, so best = 6.",
                    "The min Kadane run gives 3, -1, -7, -3, -1, so worst = -7, the piece [-1, -6].",
                    "best ≥ 0, so the answer is max(6, 2 - (-7)) = <strong>9</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest turbulent subarray
    "longest-turbulent-subarray": {
        "example": {"call": "max_turbulence_size([9, 4, 2, 10, 7, 8, 8, 1, 9])", "expect": "5"},
        "approaches": {
            "Extend from every start": {
                "idea": [
                    "In a turbulent subarray the comparisons alternate: up, down, up, … or down, up, down, ….",
                    "From each start, extend while the new comparison differs from the previous one and is not an equality.",
                ],
                "steps": [
                    "For each i, advance j while <code>arr[j] != arr[j-1]</code> and the direction flips.",
                    "Record <code>j - i</code>.",
                ],
                "why": [
                    "It checks every maximal run from every start.",
                    "It is O(n²) in the worst case and O(1) space.",
                ],
                "dry": [
                    "From 9: 9 &gt; 4, then 4 &gt; 2 does not flip, so the length is 2.",
                    "From 4: down (4 &gt; 2), up (2 &lt; 10), down (10 &gt; 7), up (7 &lt; 8), then 8 = 8 stops it. The length is <strong>5</strong>.",
                    "Later starts give shorter runs, such as 8, 1, 9 with length 3.",
                    "The result is <strong>5</strong>.",
                ],
            },
            "DP: longest run ending here going up or down": {
                "idea": [
                    "Track two numbers at each position: <code>up</code>, the longest turbulent run ending here whose last step went up, and <code>down</code>, the same ending with a down step.",
                    "A rise can only extend a run that last went down, so <code>up = down + 1</code>; a fall extends a run that last went up.",
                    "An equal pair breaks every run, so both reset to 1.",
                ],
                "steps": [
                    "Start with <code>up = down = 1</code>.",
                    "Rise: <code>up, down = down + 1, 1</code>. Fall: <code>up, down = 1, up + 1</code>. Equal: both 1.",
                    "Keep the best of up and down.",
                ],
                "why": [
                    "The two variables capture everything needed to extend a run by one element.",
                    "It is one pass: O(n) time, O(1) space.",
                ],
                "dry": [
                    "9 → 4 falls: down = 2. 4 → 2 falls again: down = up + 1 = 2.",
                    "2 → 10 rises: up = down + 1 = 3. 10 → 7 falls: down = 4. 7 → 8 rises: up = <strong>5</strong>.",
                    "8 → 8 is equal: both reset to 1. 8 → 1 falls: down = 2. 1 → 9 rises: up = 3.",
                    "The best seen is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ jump game
    "jump-game": {
        "example": {"call": "can_jump([3, 2, 1, 0, 4])", "expect": "False"},
        "approaches": {
            "Try every jump recursively": {
                "idea": [
                    "From index i you may jump 1 to <code>nums[i]</code> steps. Try every choice and succeed if any path reaches the end.",
                ],
                "steps": [
                    "<code>go(i)</code> is true if i is at or past the last index.",
                    "Otherwise try <code>go(i + k)</code> for each k from <code>nums[i]</code> down to 1.",
                ],
                "why": [
                    "It explores every path.",
                    "It is exponential, because the same indices are re-explored from many paths.",
                ],
                "dry": [
                    "go(0) tries go(3), go(2), go(1).",
                    "go(3): nums[3] = 0, so there are no jumps: False.",
                    "go(2) can only reach 3, so False. go(1) can reach 3 or 2, both False.",
                    "Every path gets stuck at the 0: <strong>False</strong>.",
                ],
            },
            "DP: which indices can reach the end": {
                "idea": [
                    "Call an index <em>good</em> if the end can be reached from it. The last index is good.",
                    "Index i is good if some jump from it lands on a good index; fill this from right to left.",
                ],
                "steps": [
                    "<code>good[n-1] = True</code>.",
                    "For i from n - 2 down: <code>good[i] = any(good[j])</code> for j in i+1..i+nums[i].",
                    "Return <code>good[0]</code>.",
                ],
                "why": [
                    "Each index is decided once, from already-decided indices to its right.",
                    "It is O(n²) time in the worst case and O(n) space.",
                ],
                "dry": [
                    "good[4] = True.",
                    "i=3: no jumps, so False. i=2: only reaches 3, so False.",
                    "i=1: reaches 2 and 3, both bad, so False. i=0: reaches 1, 2, 3, all bad, so False.",
                    "good[0] = <strong>False</strong>.",
                ],
            },
            "Greedy: pull the goal backwards": {
                "idea": [
                    "In the DP, only the <em>leftmost</em> good index matters: an index is good exactly when it can jump that far.",
                    "So keep a single <code>goal</code>, starting at the last index, and move it left to i whenever <code>i + nums[i] ≥ goal</code>.",
                ],
                "steps": [
                    "<code>goal = n - 1</code>.",
                    "For i from n - 2 down to 0: if <code>i + nums[i] &gt;= goal</code>, set <code>goal = i</code>.",
                    "Return <code>goal == 0</code>.",
                ],
                "why": [
                    "If i can reach the leftmost good index, it is good, and it becomes the new leftmost.",
                    "It is one pass: O(n) time, O(1) space.",
                ],
                "dry": [
                    "goal = 4.",
                    "i=3: 3 + 0 = 3 &lt; 4. i=2: 2 + 1 = 3 &lt; 4. i=1: 1 + 2 = 3 &lt; 4. i=0: 0 + 3 = 3 &lt; 4.",
                    "The goal never moves off 4, so the result is <strong>False</strong>.",
                ],
            },
            "Greedy: track the farthest reachable index": {
                "idea": [
                    "Walk forward keeping <code>reach</code>, the farthest index reachable so far.",
                    "Every index up to reach is reachable, because jumps can be shorter than the maximum.",
                    "If the walk ever stands on an index beyond reach, there is a gap no one can cross.",
                ],
                "steps": [
                    "<code>reach = 0</code>.",
                    "For each i: if <code>i &gt; reach</code>, return <code>False</code>; otherwise <code>reach = max(reach, i + nums[i])</code>.",
                    "Return <code>True</code>.",
                ],
                "why": [
                    "reach is exactly the furthest point any sequence of jumps through indices 0..i can get to.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "i=0: reach = 3. i=1: max(3, 3) = 3. i=2: max(3, 3) = 3. i=3: max(3, 3) = 3.",
                    "i=4: 4 &gt; reach = 3, so index 4 can never be reached.",
                    "The result is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ jump game II
    "jump-game-ii": {
        "example": {"call": "jump([2, 3, 1, 1, 4])", "expect": "2"},
        "approaches": {
            "DP: fewest jumps to each index": {
                "idea": [
                    "Let <code>jumps[j]</code> be the fewest jumps needed to reach j.",
                    "From every index i, everything it can jump to costs at most <code>jumps[i] + 1</code>.",
                ],
                "steps": [
                    "<code>jumps[0] = 0</code>, everything else infinity.",
                    "For each i, relax <code>jumps[j] = min(jumps[j], jumps[i] + 1)</code> for every j it reaches.",
                    "Return <code>jumps[-1]</code>.",
                ],
                "why": [
                    "Indices are processed left to right, so <code>jumps[i]</code> is final when it is used.",
                    "It is O(n²) time in the worst case and O(n) space.",
                ],
                "dry": [
                    "From i=0 (jump 2): jumps[1] = jumps[2] = 1.",
                    "From i=1 (jump 3): jumps[3] = 2, jumps[4] = 2.",
                    "From i=2 and i=3 nothing improves.",
                    "jumps[4] = <strong>2</strong>.",
                ],
            },
            "Greedy BFS over index ranges": {
                "idea": [
                    "The indices reachable in exactly k jumps form one contiguous range.",
                    "The next range runs up to the farthest point that any index in the current range can reach.",
                    "This is BFS where each level is an interval, so the queue is just two integers: the end of the current level and the farthest point seen.",
                ],
                "steps": [
                    "Scan i from 0 to n - 2, updating <code>farthest = max(farthest, i + nums[i])</code>.",
                    "When i reaches <code>end</code>, the current level is used up: <code>jumps += 1</code> and <code>end = farthest</code>.",
                    "Return <code>jumps</code>.",
                ],
                "why": [
                    "Each level boundary is one more jump, and levels grow as far as possible.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "i=0: farthest = 2. i equals end (0), so jumps = 1 and end = 2.",
                    "i=1: farthest = max(2, 4) = 4. i=2: farthest stays 4; i equals end, so jumps = 2 and end = 4.",
                    "i=3: farthest 4. The scan stops before the last index.",
                    "The result is <strong>2</strong>: 0 → 1 → 4.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ jump game VII
    "jump-game-vii": {
        "example": {"call": 'can_reach("011010", 2, 3)', "expect": "True"},
        "approaches": {
            "BFS, scanning each full range": {
                "idea": [
                    "From index i you may land on any '0' in <code>[i + minJump, i + maxJump]</code>.",
                    "Run BFS from 0, scanning each popped index's whole range for new reachable zeros.",
                ],
                "steps": [
                    "Queue starts with 0; <code>seen = {0}</code>.",
                    "Pop i and scan j over its range; enqueue each unseen '0'.",
                    "Return whether the last index was seen.",
                ],
                "why": [
                    "BFS finds every reachable index.",
                    "Overlapping ranges are rescanned: O(n·(maxJump - minJump)) time.",
                ],
                "dry": [
                    "Pop 0: the range is [2, 3]; s[2] = '1', s[3] = '0', so enqueue 3.",
                    "Pop 3: the range is [5, 5]; s[5] = '0', so enqueue 5.",
                    "Pop 5: its range is past the end.",
                    "5 is in seen, so the result is <strong>True</strong>.",
                ],
            },
            "BFS that never rescans (farthest pointer)": {
                "idea": [
                    "BFS pops indices in increasing order, so their ranges also start in increasing order and overlap only with what was just scanned.",
                    "Keep <code>farthest</code>, the end of everything already scanned, and start each new scan just past it.",
                    "Every index is then scanned at most once.",
                ],
                "steps": [
                    "Pop i; scan j from <code>max(i + minJump, farthest + 1)</code> to <code>min(n-1, i + maxJump)</code>.",
                    "Enqueue zeros, returning immediately if j is the last index.",
                    "Set <code>farthest = max(farthest, i + maxJump)</code>.",
                ],
                "why": [
                    "Nothing up to farthest can produce a new index, because it was all scanned already.",
                    "It is O(n) time and O(n) space.",
                ],
                "dry": [
                    "Pop 0: scan 2..3, enqueue 3. farthest = 3.",
                    "Pop 3: scan from max(5, 4) = 5 to 5; s[5] = '0' is the last index.",
                    "Return <strong>True</strong>.",
                ],
            },
            "DP with a sliding count of reachable sources": {
                "idea": [
                    "<code>ok[j]</code> is true when s[j] is '0' and some reachable i lies in <code>[j - maxJump, j - minJump]</code>.",
                    "That window of sources slides one step per j, so keep a running count of the reachable indices inside it.",
                    "Add <code>ok[j - minJump]</code> as it enters and subtract <code>ok[j - maxJump - 1]</code> as it leaves.",
                ],
                "steps": [
                    "<code>ok[0] = True</code>; <code>window = 0</code>.",
                    "For each j: update the window count, then <code>ok[j] = s[j] == '0' and window &gt; 0</code>.",
                    "Return <code>ok[-1]</code>.",
                ],
                "why": [
                    "The count is exactly the number of reachable indices that can jump to j.",
                    "It is O(1) per index: O(n) time and O(n) space.",
                ],
                "dry": [
                    "j=1: the window is empty, and s[1] = '1' anyway: False.",
                    "j=2: ok[0] enters, window = 1, but s[2] = '1': False.",
                    "j=3: ok[1] enters (no change), window = 1, and s[3] = '0': True.",
                    "j=4: ok[2] enters and ok[0] leaves, window = 0: False.",
                    "j=5: ok[3] enters and ok[1] leaves, window = 1, and s[5] = '0': True. The result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ gas station
    "gas-station": {
        "example": {"call": "can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])", "expect": "3"},
        "approaches": {
            "Simulate from every start": {
                "idea": [
                    "Try each station as the start and drive the full loop, failing as soon as the tank goes negative.",
                ],
                "steps": [
                    "For each start, add <code>gas[i] - cost[i]</code> around the loop.",
                    "Return the first start that never goes negative, otherwise -1.",
                ],
                "why": [
                    "It checks the definition directly.",
                    "It is O(n²) time and O(1) space.",
                ],
                "dry": [
                    "Starts 0, 1 and 2 fail immediately: 1 - 3, 2 - 4 and 3 - 5 are all negative.",
                    "Start 3: the tank goes 3, 6, 4, 2, 0 around the loop and never goes negative.",
                    "The result is <strong>3</strong>.",
                ],
            },
            "One pass: restart after every failure": {
                "idea": [
                    "If the total gas is less than the total cost, no start works.",
                    "Drive from a candidate start; if the tank goes negative on the way out of station i, no station between the start and i can work either, since each would reach i with no more fuel.",
                    "So jump the candidate to i + 1 and keep going. When the totals are enough, the last candidate standing is the answer.",
                ],
                "steps": [
                    "Return -1 if <code>sum(gas) &lt; sum(cost)</code>.",
                    "Accumulate <code>tank += gas[i] - cost[i]</code>; when it is negative, <code>start = i + 1</code> and <code>tank = 0</code>.",
                    "Return <code>start</code>.",
                ],
                "why": [
                    "Each skipped start is ruled out by the argument above, and the totals check guarantees the survivor can wrap around.",
                    "It is one pass: O(n) time, O(1) space.",
                ],
                "dry": [
                    "Totals: 15 vs 15, so continue.",
                    "i=0: tank -2, so start = 1. i=1: -2, so start = 2. i=2: -2, so start = 3.",
                    "i=3: tank 3. i=4: tank 6.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ hand of straights
    "hand-of-straights": {
        "example": {"call": "is_n_straight_hand([1, 2, 3, 6, 2, 3, 4, 7, 8], 3)", "expect": "True"},
        "approaches": {
            "Sort, then build groups from the smallest card": {
                "idea": [
                    "The smallest remaining card must be the start of some group, because nothing smaller is left to come before it.",
                    "So repeatedly take the smallest card and claim the next k - 1 consecutive values; if any is missing, it is impossible.",
                ],
                "steps": [
                    "Reject unless <code>len(hand) % k == 0</code>.",
                    "Count the cards; walk the distinct values in sorted order.",
                    "While value v still has copies, take one each of v..v+k-1, failing on a missing card.",
                ],
                "why": [
                    "The smallest card has no other option, so the greedy choice is forced.",
                    "It is O(n log n) for the sort plus O(n·k) for building groups card by card.",
                ],
                "dry": [
                    "Counts: 1:1, 2:2, 3:2, 4:1, 6:1, 7:1, 8:1.",
                    "v=1 starts a group 1, 2, 3, leaving 2:1 and 3:1.",
                    "v=2 starts a group 2, 3, 4.",
                    "v=3 and v=4 are used up. v=6 starts 6, 7, 8.",
                    "All cards are used: <strong>True</strong>.",
                ],
            },
            "Start whole batches of groups at once": {
                "idea": [
                    "If the smallest value v has c copies, exactly c groups must start at v.",
                    "So subtract c from each of v..v+k-1 in one go, failing if any of them has fewer than c copies.",
                ],
                "steps": [
                    "For each distinct v in sorted order with <code>c = count[v] &gt; 0</code>:",
                    "Check that <code>count[x] &gt;= c</code> for x in v..v+k-1, and subtract c from each.",
                    "Return <code>True</code> if the walk completes.",
                ],
                "why": [
                    "This is the same forced choice, applied to all copies at once.",
                    "Each distinct value is touched at most k times and the sort dominates: O(n log n).",
                ],
                "dry": [
                    "v=1, c=1: subtract 1 from 1, 2, 3.",
                    "v=2, c=1: subtract from 2, 3, 4.",
                    "v=3 and v=4 now have c = 0, so they are skipped.",
                    "v=6, c=1: subtract from 6, 7, 8. The result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ dota2 senate
    "dota2-senate": {
        "example": {"call": 'predict_party_victory("DDRRR")', "expect": '"Dire"'},
        "approaches": {
            "Simulate with a list and deletions": {
                "idea": [
                    "The best move for any senator is to ban the next opponent who would act, the one who would otherwise ban a teammate soonest.",
                    "Simulate that literally: go around the circle and delete the next opposing senator after each one.",
                ],
                "steps": [
                    "While both parties remain: for the senator at i, search forward (wrapping) for the next opponent and delete them.",
                    "Fix up i if the deleted position was before it, then move on.",
                ],
                "why": [
                    "Banning the nearest upcoming opponent is optimal, since it removes the most immediate threat.",
                    "Each deletion is O(n): O(n²) total.",
                ],
                "dry": [
                    "[D, D, R, R, R]: the first D bans the first R, leaving [D, D, R, R].",
                    "The second D bans the next R, leaving [D, D, R].",
                    "The remaining R wraps around and bans the first D, leaving [D, R].",
                    "The D bans that R, leaving [D]. The result is <strong>\"Dire\"</strong>.",
                ],
            },
            "Two queues of turn indices": {
                "idea": [
                    "Keep each party's senators in a queue of their turn indices.",
                    "The earlier of the two fronts acts first, bans the other front for good, and rejoins its own queue with index + n, its turn in the next round.",
                    "When one queue empties, the other party wins.",
                ],
                "steps": [
                    "Build queues r and d of indices.",
                    "Pop both fronts; the smaller index wins and is appended back with + n.",
                    "Return the party whose queue is non-empty.",
                ],
                "why": [
                    "Each comparison is exactly one ban, made by whoever acts first.",
                    "There are fewer than n bans, each O(1): O(n) time and O(n) space.",
                ],
                "dry": [
                    "r = [2, 3, 4], d = [0, 1], n = 5.",
                    "D0 vs R2: D acts and bans R2, and rejoins as 5. r = [3, 4], d = [1, 5].",
                    "D1 vs R3: D bans and rejoins as 6. r = [4], d = [5, 6].",
                    "R4 vs D5: R acts first and bans D5, and rejoins as 9. r = [9], d = [6].",
                    "D6 vs R9: D bans R9. r is empty, so the result is <strong>\"Dire\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge triplets
    "merge-triplets": {
        "example": {"call": "merge_triplets([[2, 5, 3], [1, 8, 4], [1, 7, 5]], [2, 7, 5])", "expect": "True"},
        "approaches": {
            "Try every subset": {
                "idea": [
                    "Merging only ever takes coordinate-wise maxima, so the result of merging a set of triplets does not depend on the order.",
                    "Therefore try every non-empty subset and check whether its coordinate-wise maximum equals the target.",
                ],
                "steps": [
                    "For each subset size r and each subset, compute the max in each of the 3 positions.",
                    "Return <code>True</code> if any equals the target.",
                ],
                "why": [
                    "It covers every reachable triplet.",
                    "There are 2<sup>n</sup> subsets: exponential.",
                ],
                "dry": [
                    "Single triplets: none equals [2, 7, 5].",
                    "[2, 5, 3] with [1, 8, 4] gives [2, 8, 4]: no.",
                    "[2, 5, 3] with [1, 7, 5] gives [2, 7, 5]: yes, so the result is <strong>True</strong>.",
                ],
            },
            "Keep the safe triplets, check each coordinate is hit": {
                "idea": [
                    "Any triplet with a value <em>above</em> the target can never be used, because a max can only go up.",
                    "Merging all the remaining safe triplets gives the largest result that stays at or below the target.",
                    "So the target is reachable exactly when every position is matched exactly by some safe triplet.",
                ],
                "steps": [
                    "For each triplet with all values ≤ the target, record which positions equal the target.",
                    "Return whether all three positions were hit.",
                ],
                "why": [
                    "Safe triplets never overshoot, and each position needs at least one triplet to reach its target value.",
                    "It is one pass: O(n) time and O(1) space.",
                ],
                "dry": [
                    "[2, 5, 3] is safe and matches position 0, so hit = {0}.",
                    "[1, 8, 4] has 8 &gt; 7, so it is unsafe and skipped.",
                    "[1, 7, 5] is safe and matches positions 1 and 2, so hit = {0, 1, 2}.",
                    "All three are hit: <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ partition labels
    "partition-labels": {
        "example": {"call": 'partition_labels("ababcbacadefegdehijhklij")', "expect": "[9, 7, 8]"},
        "approaches": {
            "Letter spans as intervals, then merge": {
                "idea": [
                    "Each letter occupies the interval from its first to its last occurrence, and all of it must sit inside one part.",
                    "Letters whose intervals overlap must therefore share a part, so merge the overlapping intervals.",
                    "Each merged interval is one part. This is the Merge Intervals problem in disguise.",
                ],
                "steps": [
                    "Record each letter's first and last index.",
                    "Sort the spans by start and merge overlapping ones.",
                    "Emit the length of each merged span.",
                ],
                "why": [
                    "Merged spans are the smallest possible parts that keep every letter whole, which gives the largest number of parts.",
                    "It is O(n) time plus sorting at most 26 spans.",
                ],
                "dry": [
                    "The spans include a(0, 8), b(1, 5), c(4, 7), d(9, 14), e(10, 15), h(16, 19), i(17, 22), j(18, 23), among others.",
                    "a, b, c merge into [0, 8], size 9.",
                    "d, e, f, g merge into [9, 15], size 7.",
                    "h, i, j, k, l merge into [16, 23], size 8.",
                    "The result is <strong>[9, 7, 8]</strong>.",
                ],
            },
            "One sweep extending the current part's end": {
                "idea": [
                    "Remember each letter's last index. Sweep left to right, stretching the current part's <code>end</code> to cover the last occurrence of every letter seen.",
                    "When the sweep reaches <code>end</code>, nothing inside the part appears later: cut here.",
                    "Cutting at the earliest possible point gives the most parts.",
                ],
                "steps": [
                    "<code>last = {ch: i}</code>.",
                    "For each i: <code>end = max(end, last[ch])</code>; if <code>i == end</code>, record the size and start a new part at i + 1.",
                ],
                "why": [
                    "The part cannot end before the last occurrence of any letter in it, and it ends exactly there.",
                    "It is O(n) time and O(Σ) space.",
                ],
                "dry": [
                    "Starting with a (last at 8), end = 8. b, c and a's later copies stay within 8.",
                    "At i=8 the sweep reaches end: cut a part of size <strong>9</strong>.",
                    "d (last 14), then e (last 15), so end = 15. At i=15, cut a part of size <strong>7</strong>.",
                    "h (19), i (22), j (23) stretch end to 23. At i=23, cut a part of size <strong>8</strong>.",
                    "The result is <strong>[9, 7, 8]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid parenthesis string
    "valid-parenthesis-string": {
        "example": {"call": 'check_valid_string("((*)")', "expect": "True"},
        "approaches": {
            "Try every assignment of the stars": {
                "idea": [
                    "Each <code>*</code> can be '(', ')' or nothing. Try all three, tracking the number of unmatched '('.",
                    "A count that goes negative is a dead end; at the end the count must be 0.",
                ],
                "steps": [
                    "<code>go(i, open_)</code>: fail if <code>open_ &lt; 0</code>; at the end, succeed if it is 0.",
                    "'(' adds 1, ')' subtracts 1, and '*' branches three ways.",
                ],
                "why": [
                    "It explores every way of reading the stars.",
                    "It is O(3<sup>k</sup>·n) for k stars.",
                ],
                "dry": [
                    "\"((\" gives open = 2, then the star branches.",
                    "Star as '(': open 3, then ')' leaves 2 at the end, which fails.",
                    "Star as ')': open 1, then ')' leaves 0 at the end, which succeeds.",
                    "The result is <strong>True</strong>.",
                ],
            },
            "DP over (index, open count)": {
                "idea": [
                    "The recursion's state is just (position, open count), with at most n × n combinations.",
                    "Memoising it means each state is solved once, which removes the exponential blow-up.",
                ],
                "steps": [
                    "Same recursion as before, wrapped in <code>@cache</code>.",
                ],
                "why": [
                    "Identical states give identical answers, so caching is safe.",
                    "It is O(n²) states with O(1) work each.",
                ],
                "dry": [
                    "go(0, 0) → go(1, 1) → go(2, 2) for the star.",
                    "go(3, 3) → go(4, 2) is False, and that is cached.",
                    "go(3, 1) → go(4, 0) is True.",
                    "The result is <strong>True</strong>; no state repeats on such a short input, but on long strings the cache is what saves the time.",
                ],
            },
            "Two stacks of indices": {
                "idea": [
                    "Match each ')' with the nearest open '(' if there is one, otherwise with a star.",
                    "Leftover '(' then need a star that comes <em>after</em> them to close them, so pair them from the top of both stacks and check the positions.",
                ],
                "steps": [
                    "Push indices of '(' and '*' onto two stacks; ')' pops an open first, else a star, else fails.",
                    "Then, while both stacks have entries, pop one of each; fail if the '(' comes after the star.",
                    "Valid if no '(' remain.",
                ],
                "why": [
                    "Using real '(' first keeps stars free for later, and checking positions ensures each leftover '(' really is closed by a star after it.",
                    "It is O(n) time and O(n) space.",
                ],
                "dry": [
                    "Indices 0 and 1 are '(', so opens = [0, 1]. Index 2 is '*', so stars = [2].",
                    "Index 3 is ')', which pops open 1. opens = [0].",
                    "Leftover: open 0 with star 2; 0 &lt; 2, so the star closes it.",
                    "opens is empty, so the result is <strong>True</strong>.",
                ],
            },
            "Greedy range of possible open counts": {
                "idea": [
                    "Instead of tracking every possible open count, track the smallest (<code>lo</code>) and largest (<code>hi</code>) possible counts.",
                    "'(' raises both and ')' lowers both; '*' lowers lo (reading it as ')') and raises hi (reading it as '(').",
                    "If hi goes negative, even all-'(' cannot save it. Clamp lo at 0, since a negative count is never a real option. Valid when lo ends at 0.",
                ],
                "steps": [
                    "Update lo and hi per character.",
                    "Fail if <code>hi &lt; 0</code>; set <code>lo = max(lo, 0)</code>.",
                    "Return <code>lo == 0</code>.",
                ],
                "why": [
                    "Every count between lo and hi is achievable by some choice of stars, so two numbers summarise all 3<sup>k</sup> options.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "'(': lo = 1, hi = 1. '(': lo = 2, hi = 2.",
                    "'*': lo = 1, hi = 3.",
                    "')': lo = 0, hi = 2.",
                    "lo ends at 0, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ candy
    "candy": {
        "example": {"call": "candy([1, 2, 3, 2, 1, 0])", "expect": "13"},
        "approaches": {
            "Relax until stable": {
                "idea": [
                    "Start everyone at 1 candy. Whenever a higher-rated child does not have more than a neighbour, raise it to one more than that neighbour.",
                    "Repeat full passes until nothing changes.",
                ],
                "steps": [
                    "For each child, check both neighbours and fix any violation.",
                    "Loop while any pass made a change.",
                ],
                "why": [
                    "Values only go up, and every fix is forced, so the stable state is the minimum.",
                    "A long slope can need up to n passes: O(n²).",
                ],
                "dry": [
                    "Pass 1: [1, 2, 3, 2, 2, 1].",
                    "Pass 2: index 3 (rating 2) must beat index 4: [1, 2, 3, 3, 2, 1].",
                    "Pass 3: index 2 (rating 3) must now beat index 3: [1, 2, 4, 3, 2, 1].",
                    "Pass 4 changes nothing. The sum is <strong>13</strong>.",
                ],
            },
            "Two sweeps": {
                "idea": [
                    "Split the rule into its two halves: beat your left neighbour, and beat your right neighbour.",
                    "A left-to-right sweep enforces the left rule; a right-to-left sweep enforces the right rule while keeping the larger of the two requirements.",
                ],
                "steps": [
                    "Left to right: if <code>ratings[i] &gt; ratings[i-1]</code>, set <code>c[i] = c[i-1] + 1</code>.",
                    "Right to left: if <code>ratings[i] &gt; ratings[i+1]</code>, set <code>c[i] = max(c[i], c[i+1] + 1)</code>.",
                    "Return <code>sum(c)</code>.",
                ],
                "why": [
                    "Each value ends as the smallest number satisfying both sides, and the second sweep never breaks the first rule.",
                    "It is O(n) time and O(n) space.",
                ],
                "dry": [
                    "Left sweep: [1, 2, 3, 1, 1, 1].",
                    "Right sweep: index 4 becomes 2, index 3 becomes 3, index 2 becomes max(3, 4) = 4.",
                    "The result is [1, 2, 4, 3, 2, 1], summing to <strong>13</strong>.",
                ],
            },
            "One pass counting slopes": {
                "idea": [
                    "On a rising run the candies are 1, 2, 3, …; on a falling run they are the same numbers read backwards.",
                    "Walk the ratings, counting the length of the current up-run and down-run, and add each child's candies as you go.",
                    "The peak between a rise and a fall belongs to the longer run: when the fall gets longer than the rise, the peak needs one extra candy.",
                ],
                "steps": [
                    "Rising: <code>up += 1</code>, <code>peak = up</code>, add <code>up + 1</code>.",
                    "Equal: reset everything and add 1.",
                    "Falling: <code>down += 1</code>, and add <code>down</code>, plus 1 when <code>down &gt; peak</code> (the peak grows).",
                ],
                "why": [
                    "It adds the same totals as the two sweeps, but as arithmetic series, without storing anything.",
                    "It is O(n) time and O(1) space, with trickier bookkeeping.",
                ],
                "dry": [
                    "Start: total = 1. The rises 1 → 2 → 3 add 2 and 3, so total = 6 and peak = 2.",
                    "First fall: down = 1, add 1, total 7. Second fall: down = 2, add 2, total 9.",
                    "Third fall: down = 3 &gt; peak = 2, so add 3 + 1 (the peak at rating 3 must grow from 3 to 4). Total 13.",
                    "The result is <strong>13</strong>.",
                ],
            },
        },
    },
}
