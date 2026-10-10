"""Write-ups for the Two Pointers and Intervals topic (sorting)."""

EXPLAIN = {
    # ------------------------------------------------------------------ reverse string
    "reverse-string": {
        "examples": [
            {"setup": 's = list("hello")\nreverse_string(s)', "call": "s",
             "expect": "['o', 'l', 'l', 'e', 'h']"},
            {"setup": 's = list("abcd")\nreverse_string(s)', "call": "s",
             "expect": "['d', 'c', 'b', 'a']"},
        ],
        "approaches": {
            "Push onto a stack, pop back": {
                "idea": [
                    "A stack hands items back in the opposite order to the one they went in, which is exactly what reversing needs.",
                    "Copy every character onto a stack, then pop them back into the list starting from index 0.",
                ],
                "steps": [
                    "Build <code>stack = list(s)</code>: a full copy, with the last character on top.",
                    "Loop <code>i</code> from 0 to <code>len(s) - 1</code>.",
                    "Write <code>s[i] = stack.pop()</code>: the top of the stack is the character that belongs at position <code>i</code>.",
                    "Nothing is returned; the list <code>s</code> itself has been overwritten in reverse order.",
                ],
                "why": [
                    "The k-th pop returns the k-th character from the end, and it is written to index k − 1, which is where the reversed list needs it.",
                    "Reading from the copy, not from <code>s</code>, matters: <code>s</code> is being overwritten while we go, so its own values would be clobbered.",
                    "Each character is pushed once and popped once: <strong>O(n)</strong> time. The stack is a full copy of the input, so space is <strong>O(n)</strong>, which breaks the problem's in-place rule.",
                ],
                "dry": [
                    [
                        "stack = [h, e, l, l, o], with o on top.",
                        "i=0: pop o, s[0] = o. i=1: pop l, s[1] = l.",
                        "i=2: pop l. i=3: pop e. i=4: pop h, and the stack is empty.",
                        "s becomes <strong>['o', 'l', 'l', 'e', 'h']</strong>.",
                    ],
                    [
                        "stack = [a, b, c, d], with d on top.",
                        "i=0: s[0] = d. i=1: s[1] = c.",
                        "i=2: s[2] = b. i=3: s[3] = a.",
                        "s becomes <strong>['d', 'c', 'b', 'a']</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just write <code>s = s[::-1]</code>?",
                     "That rebinds the local name to a new list; the caller's list is untouched. <code>s[:] = s[::-1]</code> would work, but it still builds an O(n) copy."],
                    ["Why copy into <code>stack</code> instead of popping from <code>s</code> directly?",
                     "Popping from <code>s</code> would shrink the very list you are writing into. The copy keeps the original order safe while <code>s</code> is overwritten."],
                    ["Is this accepted if the problem says O(1) extra memory?",
                     "No. It is a correct reversal, but the stack is a second copy of the input, so it only serves as a stepping stone to the two-pointer swap."],
                ],
            },
            "Recursive swap of the ends": {
                "idea": [
                    "Reversing means the first and last characters trade places, then the second and second-to-last, and so on towards the middle.",
                    "That is a recursive shape: swap the two ends, then reverse the part strictly between them.",
                ],
                "steps": [
                    "Define <code>go(lo, hi)</code>, which reverses <code>s[lo..hi]</code>.",
                    "If <code>lo &lt; hi</code>, swap <code>s[lo]</code> and <code>s[hi]</code>.",
                    "Then call <code>go(lo + 1, hi - 1)</code> for the inner part.",
                    "When <code>lo &gt;= hi</code> the part has length 0 or 1 and is already reversed, so the call does nothing.",
                    "Start with <code>go(0, len(s) - 1)</code>.",
                ],
                "why": [
                    "Each call puts the two outermost unfinished positions into their final places, and the inner call handles the rest, so by induction the whole range ends up reversed.",
                    "There are about n/2 calls, each doing one swap: <strong>O(n)</strong> time.",
                    "No data is copied, but the n/2 calls are all on the call stack at the deepest point, which is <strong>O(n)</strong> hidden space.",
                ],
                "dry": [
                    [
                        "go(0, 4): swap h and o, giving \"oellh\".",
                        "go(1, 3): swap e and l, giving \"olleh\".",
                        "go(2, 2): lo == hi, the middle l stays put. The calls unwind.",
                        "s is <strong>['o', 'l', 'l', 'e', 'h']</strong>.",
                    ],
                    [
                        "go(0, 3): swap a and d, giving \"dbca\".",
                        "go(1, 2): swap b and c, giving \"dcba\".",
                        "go(2, 1): lo &gt; hi, so there is no middle character and the recursion stops.",
                        "s is <strong>['d', 'c', 'b', 'a']</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the stop condition <code>lo &lt; hi</code> and not <code>lo != hi</code>?",
                     "With an even length the pointers cross without ever being equal (2 and 1 in \"abcd\"). <code>lo != hi</code> would keep going and undo the swaps."],
                    ["Does the recursion break on long strings?",
                     "Yes. CPython's default recursion limit is about 1000 frames, so a list of a few thousand characters raises RecursionError."],
                    ["Is this tail-recursive, and does that help?",
                     "The recursive call is the last thing done, but Python does not optimise tail calls, so every frame is still kept. Rewrite it as a loop to get O(1) space."],
                ],
            },
            "Two pointers, swap inward": {
                "idea": [
                    "The same swaps as the recursion, written as a loop: one index at each end, walking towards each other.",
                    "Only the two indices are stored, so the reversal really is in place.",
                ],
                "steps": [
                    "Set <code>lo, hi = 0, len(s) - 1</code>.",
                    "While <code>lo &lt; hi</code>, swap <code>s[lo]</code> and <code>s[hi]</code> with a tuple assignment.",
                    "Move both: <code>lo + 1</code> and <code>hi - 1</code>.",
                    "Stop when the pointers meet (odd length) or cross (even length).",
                ],
                "why": [
                    "After k swaps the first k and last k positions hold their final characters, and the loop only touches the unfinished middle.",
                    "When <code>lo &gt;= hi</code> at most one character is left unswapped, and it is the middle one, which stays where it is.",
                    "There are ⌊n/2⌋ swaps: <strong>O(n)</strong> time. Two integers are the only extra state: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0, hi=4: swap h and o, giving \"oellh\".",
                        "lo=1, hi=3: swap e and l, giving \"olleh\".",
                        "lo=2, hi=2: the loop stops; the middle l is already right.",
                        "s is <strong>['o', 'l', 'l', 'e', 'h']</strong>.",
                    ],
                    [
                        "lo=0, hi=3: swap a and d, giving \"dbca\".",
                        "lo=1, hi=2: swap b and c, giving \"dcba\".",
                        "lo=2, hi=1: the pointers have crossed, so the loop ends.",
                        "s is <strong>['d', 'c', 'b', 'a']</strong>.",
                    ],
                ],
                "faq": [
                    ["Does the tuple swap <code>s[lo], s[hi] = s[hi], s[lo]</code> need a temp variable?",
                     "No. Python evaluates the right-hand side into a tuple first, then assigns, so both old values are captured before either is overwritten."],
                    ["What happens with an empty list or one character?",
                     "<code>hi</code> starts at −1 or 0, so <code>lo &lt; hi</code> is false at once and nothing is touched, which is correct."],
                    ["Why not loop <code>i</code> over <code>range(len(s) // 2)</code> and swap with <code>s[-1 - i]</code>?",
                     "That is the same algorithm with one index; it is fine. Two named pointers just make the pattern reusable for palindrome checks and partitioning."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid palindrome
    "valid-palindrome": {
        "examples": [
            {"call": 'is_palindrome("Race, car!")', "expect": "True"},
            {"call": 'is_palindrome("0P")', "expect": "False"},
        ],
        "approaches": {
            "Clean, then compare with the reverse": {
                "idea": [
                    "The rules say to ignore case and anything that is not a letter or digit, so first produce exactly the characters that count.",
                    "After that the question is the textbook one: does the cleaned sequence read the same backwards?",
                ],
                "steps": [
                    "Build <code>clean</code>: every <code>ch</code> of <code>s</code> for which <code>ch.isalnum()</code> is true, lowercased.",
                    "Reverse it with <code>clean[::-1]</code>.",
                    "Return whether <code>clean == clean[::-1]</code>.",
                    "An input with no letters or digits gives an empty list, which equals its reverse, so it counts as a palindrome.",
                ],
                "why": [
                    "Filtering and lowercasing turn the problem's custom equality into plain list equality, so comparing with the reverse is exactly the definition.",
                    "Building <code>clean</code>, reversing it and comparing are each one pass: <strong>O(n)</strong> time.",
                    "<code>clean</code> and its reverse are two new lists of up to n characters: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "s = \"Race, car!\". The comma, the space and the ! are dropped.",
                        "clean = [r, a, c, e, c, a, r].",
                        "clean[::-1] = [r, a, c, e, c, a, r], the same list.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "s = \"0P\". Both characters are alphanumeric, so both are kept.",
                        "clean = ['0', 'p'] and clean[::-1] = ['p', '0'].",
                        "The first elements differ.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>isalnum()</code> and not <code>isalpha()</code>?",
                     "Digits count too. With <code>isalpha()</code> the input \"0P\" would be cleaned to just ['p'] and wrongly reported as a palindrome."],
                    ["Is a string of only punctuation a palindrome?",
                     "Yes. The cleaned list is empty, and an empty sequence reads the same both ways, so this returns <code>True</code>, as the problem expects for inputs like \" \"."],
                    ["Could I build a string instead of a list?",
                     "<code>\"\".join(...)</code> works the same and is also O(n). The comparison cost and the memory are the same either way."],
                ],
            },
            "Two pointers skipping non-alphanumerics": {
                "idea": [
                    "Instead of building a cleaned copy, compare from both ends of the original string and simply step over characters that do not count.",
                    "Each loop iteration does one of three things: skip on the left, skip on the right, or compare a real pair.",
                ],
                "steps": [
                    "Set <code>lo, hi = 0, len(s) - 1</code>.",
                    "While <code>lo &lt; hi</code>: if <code>s[lo]</code> is not alphanumeric, move <code>lo</code> right and go round again.",
                    "Else if <code>s[hi]</code> is not alphanumeric, move <code>hi</code> left and go round again.",
                    "Else compare <code>s[lo].lower()</code> with <code>s[hi].lower()</code>; if they differ, return <code>False</code>.",
                    "If they match, move both pointers inward.",
                    "When the pointers meet or cross, every real pair matched: return <code>True</code>.",
                ],
                "why": [
                    "The pointers visit the alphanumeric characters in the same order as <code>clean</code> and <code>clean[::-1]</code> would, so each comparison is the same pair the copy-based version checks.",
                    "Every iteration moves at least one pointer one step, and they start n − 1 apart, so there are fewer than n iterations: <strong>O(n)</strong> time.",
                    "Only two indices are stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0 'R', hi=9 '!': the right side is not alphanumeric, hi=8.",
                        "'R' vs 'r': equal after lower(). lo=1, hi=7: 'a' vs 'a'. lo=2, hi=6: 'c' vs 'c'.",
                        "lo=3 'e', hi=5 ' ': skip, hi=4 ',': skip, hi=3.",
                        "lo == hi, so the loop ends: <strong>True</strong>.",
                    ],
                    [
                        "lo=0 '0', hi=1 'P': both are alphanumeric.",
                        "'0' vs 'p' differ.",
                        "It returns <strong>False</strong> straight away.",
                    ],
                ],
                "faq": [
                    ["Why use <code>if / elif / elif / else</code> instead of inner <code>while</code> loops for skipping?",
                     "Each pass of the outer loop re-checks <code>lo &lt; hi</code>, so a pointer can never skip past the other one. Inner loops need their own bound check to be safe."],
                    ["Why lower both characters instead of comparing with <code>casefold()</code>?",
                     "The problem is ASCII-only, where <code>lower()</code> is enough. <code>casefold()</code> matters only for special Unicode cases such as the German ß."],
                    ["What does it return for \".,\"?",
                     "Both characters are skipped, the pointers cross with nothing compared, and it returns <code>True</code>, same as the cleaned version."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid palindrome II
    "valid-palindrome-ii": {
        "examples": [
            {"call": 'valid_palindrome("abcbea")', "expect": "True"},
            {"call": 'valid_palindrome("abxcyba")', "expect": "False"},
        ],
        "approaches": {
            "Try deleting each character": {
                "idea": [
                    "At most one deletion is allowed, so there are only n + 1 candidate strings: the original and the n strings with one character removed.",
                    "Test each candidate with the plain reverse check and stop at the first palindrome.",
                ],
                "steps": [
                    "If <code>s == s[::-1]</code>, no deletion is needed: return <code>True</code>.",
                    "Loop <code>i</code> over every index.",
                    "Build <code>t = s[:i] + s[i + 1:]</code>, the string without character <code>i</code>.",
                    "If <code>t == t[::-1]</code>, return <code>True</code>.",
                    "If no deletion works, return <code>False</code>.",
                ],
                "why": [
                    "Every way of deleting zero or one character is tried, so the answer cannot be missed.",
                    "Each of the n candidates costs O(n) to build and O(n) to compare: <strong>O(n²)</strong> time.",
                    "Only one candidate and its reverse exist at a time: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "\"abcbea\" reversed is \"aebcba\", not equal.",
                        "i=0: \"bcbea\", no. i=1: \"acbea\", no. i=2: \"abbea\", no.",
                        "i=3: \"abcea\", no.",
                        "i=4: \"abcba\" is a palindrome, so it returns <strong>True</strong>.",
                    ],
                    [
                        "\"abxcyba\" is not a palindrome.",
                        "i=0..2: \"bxcyba\", \"axcyba\", \"abcyba\": none read the same backwards.",
                        "i=3..6: \"abxyba\", \"abxcba\", \"abxcya\", \"abxcyb\": none either.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check the original string first?",
                     "\"At most one\" includes zero deletions. The loop alone would also catch most such cases, but checking first is clearer and returns sooner."],
                    ["Is the first check actually needed for correctness?",
                     "No, for any non-empty input: deleting the middle character of an odd palindrome, or either middle character of an even one, keeps it a palindrome. It is there for clarity and speed."],
                    ["Why is this too slow?",
                     "With n = 10⁵ it builds 10⁵ strings of length 10⁵, about 10¹⁰ character operations. The two-pointer version shows only two candidates ever matter."],
                ],
            },
            "Two pointers, branch once at the first mismatch": {
                "idea": [
                    "Walk inward from both ends while characters match: matching outer pairs never need deleting.",
                    "At the first mismatch one of the two characters must go. Try both options, each with a plain palindrome check on what is left.",
                ],
                "steps": [
                    "Write a helper <code>pal(lo, hi)</code> that checks whether <code>s[lo..hi]</code> is a palindrome with the usual inward walk.",
                    "Set <code>lo, hi = 0, len(s) - 1</code> and walk inward while <code>s[lo] == s[hi]</code>.",
                    "At the first mismatch, return <code>pal(lo + 1, hi) or pal(lo, hi - 1)</code>: skip the left character, or skip the right one.",
                    "If the walk finishes without a mismatch, the string is already a palindrome: return <code>True</code>.",
                ],
                "why": [
                    "The outer pairs before the mismatch are equal, so deleting one of them never helps; the deletion has to fix the first unequal pair, and it can only remove <code>s[lo]</code> or <code>s[hi]</code>.",
                    "After choosing a side, no more deletions are allowed, so a strict palindrome check of the rest is exactly the right test.",
                    "The first walk plus at most two inner checks touch each character a constant number of times: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0, hi=5: 'a' == 'a'. Move to lo=1, hi=4.",
                        "'b' vs 'e': the first mismatch.",
                        "pal(2, 4) checks \"cbe\": 'c' vs 'e' fails.",
                        "pal(1, 3) checks \"bcb\": 'b' == 'b', then the middle. It succeeds: <strong>True</strong>.",
                    ],
                    [
                        "lo=0, hi=6: 'a' == 'a'. lo=1, hi=5: 'b' == 'b'.",
                        "lo=2, hi=4: 'x' vs 'y', the first mismatch.",
                        "pal(3, 4) checks \"cy\": fails. pal(2, 3) checks \"xc\": fails.",
                        "Neither deletion works: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must I try both sides? Can't I peek at the next character to decide?",
                     "Peeking can be fooled: both options may match the next character and only one works further in. Trying both costs just two O(n) checks, so it is the safe choice."],
                    ["Why can the helper not allow a second deletion?",
                     "The problem allows at most one. The branch already used it, so the rest must be a palindrome as it stands."],
                    ["How would this change for at most k deletions?",
                     "Branching twice per mismatch grows like 2<sup>k</sup>. For general k it becomes a DP on the longest palindromic subsequence: the answer is whether n − LPS ≤ k."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge strings alternately
    "merge-strings-alternately": {
        "examples": [
            {"call": 'merge_alternately("abcd", "pq")', "expect": '"apbqcd"'},
            {"call": 'merge_alternately("ab", "pqrs")', "expect": '"apbqrs"'},
        ],
        "approaches": {
            "Two indices": {
                "idea": [
                    "Take one letter from each word in turn while both still have letters.",
                    "Once the shorter word runs out, whatever is left of the longer word goes on the end unchanged.",
                ],
                "steps": [
                    "Start with an empty list <code>out</code> and a shared index <code>i = 0</code>.",
                    "While <code>i</code> is valid for both words, append <code>word1[i]</code> then <code>word2[i]</code>.",
                    "Increase <code>i</code> by one each round.",
                    "After the loop, join <code>out</code> and add the tails <code>word1[i:]</code> and <code>word2[i:]</code>.",
                    "At most one of the tails is non-empty, so the order of adding them does not matter.",
                ],
                "why": [
                    "The loop produces the alternating part for the first <code>min(m, n)</code> positions, and the problem says the leftover letters are appended in order, which is what the slices give.",
                    "Each letter is copied a constant number of times: <strong>O(m + n)</strong> time.",
                    "The output itself has m + n characters, and <code>out</code> holds up to that many: <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0: append a, p. out = [a, p].",
                        "i=1: append b, q. out = [a, p, b, q].",
                        "i=2: \"pq\" has no index 2, so the loop stops.",
                        "\"apbq\" + \"cd\" + \"\" = <strong>\"apbqcd\"</strong>.",
                    ],
                    [
                        "i=0: append a, p. i=1: append b, q.",
                        "i=2: \"ab\" is used up, so the loop stops.",
                        "word1[2:] is empty and word2[2:] is \"rs\".",
                        "\"apbq\" + \"\" + \"rs\" = <strong>\"apbqrs\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why a list and <code>join</code> instead of <code>result += ch</code>?",
                     "Repeated string concatenation can copy the growing string each time, which is quadratic in the worst case. Appending to a list and joining once is guaranteed linear."],
                    ["Does slicing past the end raise an error?",
                     "No. <code>word1[i:]</code> with <code>i == len(word1)</code> is just the empty string, which is why both tails can be added blindly."],
                    ["Why is this listed as two pointers when there is one index?",
                     "The single <code>i</code> stands for two pointers that always move together, one in each word. If the words were consumed at different rates you would need two."],
                ],
            },
            "zip_longest": {
                "idea": [
                    "<code>itertools.zip_longest</code> already does \"pair up position by position, keep going after the shorter one ends\".",
                    "Using an empty-string fill value makes the missing side vanish when the pair is concatenated.",
                ],
                "steps": [
                    "Call <code>zip_longest(word1, word2, fillvalue=\"\")</code> to get pairs <code>(a, b)</code>.",
                    "For each pair, form <code>a + b</code>; one of them is <code>\"\"</code> once the shorter word is finished.",
                    "Join all the pieces with <code>\"\".join</code> and return the result.",
                    "No index arithmetic or tail handling is needed; the fill value does that job.",
                ],
                "why": [
                    "Pair i holds the i-th letter of each word, so <code>a + b</code> emits them in the required alternating order; after the shorter word ends, only the longer word's letters remain in each pair.",
                    "There are <code>max(m, n)</code> pairs and each letter is copied once: <strong>O(m + n)</strong> time.",
                    "The generator holds one pair at a time, but the output string is m + n long: <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pairs: (a, p), (b, q), (c, \"\"), (d, \"\").",
                        "Pieces: \"ap\", \"bq\", \"c\", \"d\".",
                        "The fill value hides the missing letters of \"pq\".",
                        "Joined: <strong>\"apbqcd\"</strong>.",
                    ],
                    [
                        "Pairs: (a, p), (b, q), (\"\", r), (\"\", s).",
                        "Pieces: \"ap\", \"bq\", \"r\", \"s\".",
                        "This time the fill value stands in for word1.",
                        "Joined: <strong>\"apbqrs\"</strong>.",
                    ],
                ],
                "faq": [
                    ["What happens with plain <code>zip</code>?",
                     "<code>zip</code> stops at the shorter word, so \"cd\" would be lost and the answer would be \"apbq\"."],
                    ["What if I forget <code>fillvalue=\"\"</code>?",
                     "The default fill is <code>None</code>, and <code>\"c\" + None</code> raises a TypeError."],
                    ["Is this acceptable in an interview?",
                     "Usually yes as a follow-up, but expect to be asked for the index version too, since it shows you can handle the tail yourself."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge sorted array
    "merge-sorted-array": {
        "examples": [
            {"setup": "a = [1, 4, 7, 0, 0, 0]\nmerge(a, 3, [2, 5, 6], 3)", "call": "a",
             "expect": "[1, 2, 4, 5, 6, 7]"},
            {"setup": "a = [4, 5, 0, 0]\nmerge(a, 2, [1, 2], 2)", "call": "a",
             "expect": "[1, 2, 4, 5]"},
        ],
        "approaches": {
            "Copy in and sort": {
                "idea": [
                    "<code>nums1</code> already has exactly n free slots at the end, so drop <code>nums2</code> into them.",
                    "Then the list holds the right values in the wrong order, and a sort fixes the order.",
                ],
                "steps": [
                    "Assign <code>nums1[m:] = nums2</code>, overwriting the placeholder zeros.",
                    "Call <code>nums1.sort()</code>, which sorts the list in place.",
                    "Nothing is returned: the caller's list has been changed.",
                    "The fact that both halves were already sorted is not used.",
                ],
                "why": [
                    "After the copy <code>nums1</code> contains exactly the m + n values to merge, and sorting them gives the merged order by definition.",
                    "Sorting costs <strong>O((m + n) log(m + n))</strong> time in general. Python's Timsort spots the two sorted runs and merges them in near-linear time, but that is an implementation detail.",
                    "Timsort may use up to <strong>O(m + n)</strong> scratch space for merging runs; the copy itself uses none beyond <code>nums1</code>.",
                ],
                "dry": [
                    [
                        "nums1[3:] = [2, 5, 6], so a = [1, 4, 7, 2, 5, 6].",
                        "Sorting gives [1, 2, 4, 5, 6, 7].",
                        "The list is changed in place.",
                        "a is <strong>[1, 2, 4, 5, 6, 7]</strong>.",
                    ],
                    [
                        "nums1[2:] = [1, 2], so a = [4, 5, 1, 2].",
                        "Sorting gives [1, 2, 4, 5].",
                        "a is <strong>[1, 2, 4, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>nums1[m:] = nums2</code> and not <code>nums1 = nums1[:m] + nums2</code>?",
                     "The second form makes a new list and rebinds the local name; the caller never sees it. Slice assignment changes the existing list."],
                    ["Is <code>sorted(nums1)</code> fine instead of <code>nums1.sort()</code>?",
                     "Only as <code>nums1[:] = sorted(nums1)</code>. On its own <code>sorted</code> returns a new list and leaves <code>nums1</code> unchanged."],
                    ["Why would an interviewer reject this?",
                     "It ignores that both inputs are sorted, which is the whole point of the problem. The expected answer is a linear merge."],
                ],
            },
            "Copy nums1's values, merge forward": {
                "idea": [
                    "This is the merge step of merge sort: repeatedly take the smaller front element of the two sorted lists.",
                    "Writing forward into <code>nums1</code> would overwrite values not yet read, so copy <code>nums1</code>'s real values aside first.",
                ],
                "steps": [
                    "Save <code>first = nums1[:m]</code>, the m real values.",
                    "Set read indices <code>i = j = 0</code> and write index <code>k = 0</code>.",
                    "While both lists have values, write the smaller of <code>first[i]</code> and <code>nums2[j]</code> to <code>nums1[k]</code> and advance that read index.",
                    "Advance <code>k</code> after every write.",
                    "When one list runs out, copy the rest with <code>nums1[k:] = first[i:] + nums2[j:]</code>; only one of those tails is non-empty.",
                ],
                "why": [
                    "Each write takes the smallest value not yet placed, because both lists are sorted and their smallest unplaced values are at <code>i</code> and <code>j</code>.",
                    "Reading from <code>first</code> rather than <code>nums1</code> means writes can never clobber an unread value.",
                    "Every value is written once: <strong>O(m + n)</strong> time. The copy <code>first</code> is <strong>O(m)</strong> extra space.",
                ],
                "dry": [
                    [
                        "first = [1, 4, 7], nums2 = [2, 5, 6].",
                        "1 ≤ 2: write 1. 4 &gt; 2: write 2. 4 ≤ 5: write 4. k = 3.",
                        "7 &gt; 5: write 5. 7 &gt; 6: write 6. j = 3, nums2 is used up.",
                        "Tail first[2:] = [7] goes to nums1[5:]. a is <strong>[1, 2, 4, 5, 6, 7]</strong>.",
                    ],
                    [
                        "first = [4, 5], nums2 = [1, 2].",
                        "4 &gt; 1: write 1. 4 &gt; 2: write 2. nums2 is used up with i = 0.",
                        "Tail first[0:] = [4, 5] goes to nums1[2:].",
                        "a is <strong>[1, 2, 4, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;=</code> and not <code>&lt;</code> when comparing?",
                     "Either gives a correct merge. <code>&lt;=</code> takes from <code>first</code> on ties, which keeps the merge stable (equal values keep their original order)."],
                    ["What goes wrong without the copy?",
                     "In [4, 5, 0, 0] + [1, 2], writing 1 to index 0 would destroy the 4 before it is read."],
                    ["How do I avoid the O(m) copy?",
                     "Merge from the back instead. The free slots are at the end of <code>nums1</code>, so writing the largest values there never overwrites anything unread."],
                ],
            },
            "Merge backwards into the free space": {
                "idea": [
                    "The empty slots are at the <em>end</em> of <code>nums1</code>, so fill the merged list from the back, largest value first.",
                    "The write position always stays at or ahead of the read position in <code>nums1</code>, so no unread value is ever overwritten and no copy is needed.",
                ],
                "steps": [
                    "Set <code>i = m - 1</code> (last real value of nums1), <code>j = n - 1</code> (last of nums2), <code>k = m + n - 1</code> (last slot).",
                    "Loop while <code>j &gt;= 0</code>, i.e. while nums2 still has values to place.",
                    "If <code>i &gt;= 0</code> and <code>nums1[i] &gt; nums2[j]</code>, move <code>nums1[i]</code> to slot <code>k</code> and decrease <code>i</code>.",
                    "Otherwise move <code>nums2[j]</code> to slot <code>k</code> and decrease <code>j</code>.",
                    "Decrease <code>k</code> after every write.",
                ],
                "why": [
                    "Each step places the largest value not yet placed into the largest free slot, which is the merge step run in reverse.",
                    "Always <code>k = i + j + 1</code>, so <code>k ≥ i</code>: writing at <code>k</code> never destroys an unread <code>nums1</code> value.",
                    "Once <code>j</code> drops below 0, whatever is left of nums1 is already in its final place, so the loop can stop there.",
                    "At most m + n writes: <strong>O(m + n)</strong> time, and three indices: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=2 (7), j=2 (6), k=5: 7 &gt; 6, so a[5] = 7. i=1.",
                        "4 vs 6: write 6 at k=4. 4 vs 5: write 5 at k=3. j=0.",
                        "4 vs 2: write 4 at k=2, i=0. 1 vs 2: write 2 at k=1, j=−1.",
                        "The loop stops; the 1 at index 0 is already right. a is <strong>[1, 2, 4, 5, 6, 7]</strong>.",
                    ],
                    [
                        "i=1 (5), j=1 (2), k=3: 5 &gt; 2, a[3] = 5. Then 4 &gt; 2, a[2] = 4. i = −1.",
                        "a is now [4, 5, 4, 5]; nums1's values have moved to the back.",
                        "i &lt; 0, so the rest come from nums2: a[1] = 2, a[0] = 1.",
                        "a is <strong>[1, 2, 4, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why loop on <code>j &gt;= 0</code> and not on <code>i &gt;= 0 or j &gt;= 0</code>?",
                     "If nums2 runs out first, the remaining nums1 values are already sitting in their correct slots, so there is nothing left to do."],
                    ["Why is the <code>i &gt;= 0</code> check inside the condition needed?",
                     "Once nums1 is used up, <code>nums1[-1]</code> would silently read the last element of the list instead of failing, which gives wrong answers."],
                    ["What about ties?",
                     "With <code>&gt;</code>, ties take from nums2 first. Since the merge runs backwards, that leaves the equal nums1 value earlier, so the result is still stable."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ remove duplicates from sorted array
    "remove-duplicates-sorted": {
        "examples": [
            {"setup": "a = [0, 0, 1, 1, 1, 2, 2, 3]\nk = remove_duplicates(a)", "call": "(k, a[:k])",
             "expect": "(4, [0, 1, 2, 3])"},
            {"setup": "a = [2, 2, 2]\nk = remove_duplicates(a)", "call": "(k, a[:k])",
             "expect": "(1, [2])"},
        ],
        "approaches": {
            "Set, then sort back in": {
                "idea": [
                    "A set removes duplicates automatically; sorting it restores ascending order.",
                    "Then write those distinct values over the front of <code>nums</code> and report how many there are.",
                ],
                "steps": [
                    "Compute <code>uniq = sorted(set(nums))</code>.",
                    "Overwrite the front: <code>nums[:len(uniq)] = uniq</code>.",
                    "Return <code>len(uniq)</code>; anything after that index is ignored by the caller.",
                    "Slice assignment of equal length keeps the list's size unchanged.",
                ],
                "why": [
                    "The set contains each value exactly once, and sorting puts them in the order the input already had, so the first k slots are right.",
                    "Building the set is O(n), but sorting it costs <strong>O(n log n)</strong> time, even though the input was already sorted.",
                    "The set and the sorted list are <strong>O(n)</strong> extra space, which the problem disallows.",
                ],
                "dry": [
                    [
                        "set(nums) = {0, 1, 2, 3}; sorted gives [0, 1, 2, 3].",
                        "nums[:4] = [0, 1, 2, 3], so a = [0, 1, 2, 3, 1, 2, 2, 3].",
                        "It returns 4.",
                        "(k, a[:k]) is <strong>(4, [0, 1, 2, 3])</strong>.",
                    ],
                    [
                        "set(nums) = {2}; sorted gives [2].",
                        "nums[:1] = [2]; a is unchanged.",
                        "(k, a[:k]) is <strong>(1, [2])</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort the set at all?",
                     "Sets have no reliable order. The answer must list the distinct values in ascending order, as they were in the input."],
                    ["Why not <code>nums[:] = uniq</code>?",
                     "That also works for this checker, but the problem asks you to keep the array and return k; only the first k slots are judged."],
                    ["What about the elements after index k?",
                     "Leftovers from the original array. The problem says they do not matter, which is what makes an in-place answer possible."],
                ],
            },
            "Write pointer": {
                "idea": [
                    "In a sorted array, duplicates sit next to each other, so a value is new exactly when it differs from the last value kept.",
                    "Keep a write pointer <code>k</code>: <code>nums[:k]</code> is the finished distinct prefix, and each new value is written at <code>nums[k]</code>.",
                ],
                "steps": [
                    "Start with <code>k = 1</code>: the first element is always kept.",
                    "Loop <code>x</code> over the remaining elements <code>nums[1:]</code>.",
                    "If <code>x != nums[k - 1]</code>, the last kept value, it is new: write <code>nums[k] = x</code> and increase <code>k</code>.",
                    "Otherwise it is a repeat; skip it.",
                    "Return <code>k</code>.",
                ],
                "why": [
                    "Because the array is sorted, all copies of a value form one run, and only the first element of each run differs from the kept value before it.",
                    "The write pointer never passes the read position, so writes only touch slots already read.",
                    "One pass: <strong>O(n)</strong> time. As written, <code>nums[1:]</code> creates a copy; iterating by index instead keeps the extra space at <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "k=1, kept = [0]. x=0: same as nums[0], skip.",
                        "x=1: new, nums[1] = 1, k=2. The next two 1s are skipped.",
                        "x=2: new, nums[2] = 2, k=3. The second 2 is skipped.",
                        "x=3: new, nums[3] = 3, k=4. Returns 4, so the answer is <strong>(4, [0, 1, 2, 3])</strong>.",
                    ],
                    [
                        "k=1, kept = [2].",
                        "x=2: equals nums[0], skip. x=2: equals nums[0], skip.",
                        "No writes happen at all.",
                        "Returns 1: <strong>(1, [2])</strong>.",
                    ],
                ],
                "faq": [
                    ["Why compare with <code>nums[k - 1]</code> instead of the previous input element?",
                     "Both work on a sorted array, since the last kept value equals the previous element's value. Comparing with the kept value is the version that extends to \"keep at most two copies\" (compare with <code>nums[k - 2]</code>)."],
                    ["What if the array is empty?",
                     "<code>k = 1</code> would be wrong. The problem guarantees at least one element; otherwise add <code>if not nums: return 0</code>."],
                    ["Does <code>for x in nums[1:]</code> see the values I overwrite?",
                     "No: the slice is a snapshot copy taken before the loop. That is harmless here, because writes only go to slots already read, but it does cost O(n) memory."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ two sum II
    "two-sum-ii": {
        "examples": [
            {"call": "two_sum_sorted([1, 3, 4, 6, 8, 11], 10)", "expect": "[3, 4]"},
            {"call": "two_sum_sorted([-3, -1, 0, 2, 5], -4)", "expect": "[1, 2]"},
        ],
        "approaches": {
            "Every pair": {
                "idea": [
                    "Try every pair of positions <code>i &lt; j</code> and return the first whose values add up to the target.",
                    "The sorted order is not used at all; this is the baseline the faster versions improve on.",
                ],
                "steps": [
                    "Loop <code>i</code> over every index.",
                    "Loop <code>j</code> from <code>i + 1</code> to the end, so each pair is tried once and never with itself.",
                    "If <code>numbers[i] + numbers[j] == target</code>, return <code>[i + 1, j + 1]</code>.",
                    "The <code>+ 1</code>s convert to the 1-based indices the problem asks for.",
                ],
                "why": [
                    "Every pair is examined, and the problem promises exactly one solution, so the loop is guaranteed to find it.",
                    "Pairs are tried in order of <code>i</code>, then <code>j</code>, so the first match found has the smallest <code>i</code>.",
                    "There are n(n − 1)/2 pairs: <strong>O(n²)</strong> time, with two loop indices: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0 (1): sums with the rest are 4, 5, 7, 9, 12. None is 10.",
                        "i=1 (3): sums 7, 9, 11, 14. None is 10.",
                        "i=2 (4): j=3 gives 4 + 6 = 10.",
                        "It returns <strong>[3, 4]</strong>.",
                    ],
                    [
                        "i=0 (−3), j=1 (−1): −3 + (−1) = −4, a match on the very first pair.",
                        "No other pair is tried.",
                        "It returns <strong>[1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>j</code> start at <code>i + 1</code>?",
                     "Starting at 0 would try each pair twice and also pair an element with itself, which the problem forbids."],
                    ["What does this return if no pair exists?",
                     "The function falls off the end and returns <code>None</code>. The problem guarantees a solution, so that never happens in the tests."],
                    ["Is there any reason to use it?",
                     "Only as a correctness reference. With n = 3·10⁴ it does about 4.5·10⁸ checks, far too slow."],
                ],
            },
            "Binary search for each complement": {
                "idea": [
                    "For a fixed first number <code>x</code>, the partner must be exactly <code>target - x</code>.",
                    "The array is sorted, so that partner can be found by binary search instead of a linear scan.",
                ],
                "steps": [
                    "Loop over <code>i, x</code> with <code>enumerate(numbers)</code>.",
                    "Find <code>j = bisect_left(numbers, target - x, i + 1)</code>: the first position at or after <code>i + 1</code> whose value is not smaller than the complement.",
                    "If <code>j</code> is in range and <code>numbers[j] == target - x</code>, return <code>[i + 1, j + 1]</code>.",
                    "Otherwise the complement is not to the right of <code>i</code>; try the next <code>x</code>.",
                ],
                "why": [
                    "If the answer is <code>(i, j)</code>, then when the loop reaches <code>i</code>, <code>numbers[j]</code> is the complement and lies in the searched range, so bisect finds it.",
                    "Starting the search at <code>i + 1</code> stops <code>x</code> from being used twice.",
                    "n binary searches of O(log n) each: <strong>O(n log n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0, x=1: need 9. bisect lands on 11 at index 5, not 9.",
                        "i=1, x=3: need 7. bisect lands on 8 at index 4, not 7.",
                        "i=2, x=4: need 6. bisect lands on index 3, and numbers[3] = 6.",
                        "It returns <strong>[3, 4]</strong>.",
                    ],
                    [
                        "i=0, x=−3: need −1.",
                        "bisect_left from index 1 lands on index 1, and numbers[1] = −1.",
                        "It returns <strong>[1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>bisect_left</code> and not <code>bisect_right</code>?",
                     "<code>bisect_left</code> returns the position of the first copy of the value if it exists. <code>bisect_right</code> returns the position after the last copy, so you would have to check <code>j - 1</code>."],
                    ["Why the <code>j &lt; len(numbers)</code> check?",
                     "If every value is smaller than the complement, bisect returns <code>len(numbers)</code>, and indexing there would raise an IndexError."],
                    ["What if the complement equals <code>x</code> itself, as in [2, 2] with target 4?",
                     "The search starts at <code>i + 1</code>, so it finds the second 2, not the same element again."],
                ],
            },
            "Two pointers from both ends": {
                "idea": [
                    "Put one pointer on the smallest value and one on the largest, and look at their sum.",
                    "If the sum is too small, only a bigger left value can help, so move <code>lo</code> right. If too big, move <code>hi</code> left. Each move rules out a whole row or column of pairs.",
                ],
                "steps": [
                    "Set <code>lo, hi = 0, len(numbers) - 1</code>.",
                    "While <code>lo &lt; hi</code>, compute <code>total = numbers[lo] + numbers[hi]</code>.",
                    "If <code>total == target</code>, return <code>[lo + 1, hi + 1]</code>.",
                    "If <code>total &lt; target</code>, increase <code>lo</code>.",
                    "Otherwise (<code>total &gt; target</code>), decrease <code>hi</code>.",
                ],
                "why": [
                    "If <code>total &lt; target</code>, then <code>numbers[lo]</code> plus any value at or left of <code>hi</code> is also too small, so <code>lo</code> can never be part of the answer and is safely dropped. The mirror argument covers <code>hi</code>.",
                    "So the answer pair is never discarded, and since one pointer moves each step, the pointers reach it.",
                    "At most n − 1 steps: <strong>O(n)</strong> time. Two indices: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0 (1), hi=5 (11): 12 &gt; 10, so hi=4.",
                        "1 + 8 = 9 &lt; 10, lo=1. 3 + 8 = 11 &gt; 10, hi=3.",
                        "3 + 6 = 9 &lt; 10, lo=2. 4 + 6 = 10.",
                        "It returns <strong>[3, 4]</strong>.",
                    ],
                    [
                        "lo=0 (−3), hi=4 (5): 2 &gt; −4, hi=3.",
                        "−3 + 2 = −1 &gt; −4, hi=2. −3 + 0 = −3 &gt; −4, hi=1.",
                        "−3 + (−1) = −4: found, with <code>hi</code> doing all the moving.",
                        "It returns <strong>[1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is it safe to throw away <code>lo</code> when the sum is too small?",
                     "<code>numbers[hi]</code> is the largest value still in play. If even that is not enough with <code>numbers[lo]</code>, no remaining partner is."],
                    ["Does this need the array to be sorted?",
                     "Yes. The whole argument rests on \"moving left makes the sum smaller, moving right makes it bigger\". On unsorted input use a hash map instead."],
                    ["Why <code>lo &lt; hi</code> and not <code>lo &lt;= hi</code>?",
                     "When <code>lo == hi</code> the pair would use the same element twice, which is not allowed."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ 3Sum
    "three-sum": {
        "examples": [
            {"call": "sorted(sorted(t) for t in three_sum([-1, 0, 1, 2, -1, -4]))",
             "expect": "[[-1, -1, 2], [-1, 0, 1]]"},
            {"call": "sorted(sorted(t) for t in three_sum([0, 0, 0, 0]))", "expect": "[[0, 0, 0]]"},
        ],
        "approaches": {
            "Every triple, deduplicated with a set": {
                "idea": [
                    "Check every choice of three positions and keep the ones that sum to zero.",
                    "The same values can appear at different positions, so store each triple in sorted form inside a set to drop repeats.",
                ],
                "steps": [
                    "Create an empty set <code>found</code>.",
                    "Loop over <code>itertools.combinations(nums, 3)</code>, which yields every triple of positions once.",
                    "If <code>a + b + c == 0</code>, add <code>tuple(sorted((a, b, c)))</code> to <code>found</code>.",
                    "Sorting makes (−1, 2, −1) and (−1, −1, 2) the same key.",
                    "Return the set's tuples as lists.",
                ],
                "why": [
                    "Every possible triple is tested, so no answer is missed, and the sorted-tuple key collapses any triple with the same values into one entry.",
                    "There are n choose 3 triples: <strong>O(n³)</strong> time.",
                    "The set holds one entry per distinct answer: <strong>O(k)</strong> space for k answers.",
                ],
                "dry": [
                    [
                        "There are 20 triples of positions.",
                        "Zero-sum ones: (−1, 0, 1), (−1, 2, −1) and (0, 1, −1).",
                        "Sorted, they become (−1, 0, 1), (−1, −1, 2) and (−1, 0, 1) again, so the set keeps two.",
                        "The normalised answer is <strong>[[-1, -1, 2], [-1, 0, 1]]</strong>.",
                    ],
                    [
                        "There are 4 triples of positions, all (0, 0, 0).",
                        "Each sums to zero, but the set keeps one copy.",
                        "The answer is <strong>[[0, 0, 0]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort each triple before adding it?",
                     "The set compares tuples exactly, so (−1, 0, 1) and (0, 1, −1) would both be kept. Sorting gives one canonical form per group of values."],
                    ["Does <code>combinations</code> reuse an element?",
                     "No. It picks three different positions, so values only repeat if they really appear more than once."],
                    ["Why is the output order different from the other approaches?",
                     "Set order is arbitrary. The problem accepts any order, which is why the worked example sorts the result before comparing."],
                ],
            },
            "Fix one, hash set for the other two": {
                "idea": [
                    "Fix the first number <code>nums[i]</code>; the other two must sum to <code>-nums[i]</code>. That is Two Sum.",
                    "Solve that Two Sum on the elements after <code>i</code> with a set of values seen so far, and dedupe the answers with a set of sorted tuples.",
                ],
                "steps": [
                    "Create <code>found = set()</code>.",
                    "For each <code>i</code>, start a fresh <code>seen = set()</code>.",
                    "Scan <code>x</code> over <code>nums[i + 1:]</code>. The needed partner is <code>-nums[i] - x</code>.",
                    "If the partner is in <code>seen</code>, add the sorted triple to <code>found</code>.",
                    "Add <code>x</code> to <code>seen</code> and continue; at the end return <code>found</code> as lists.",
                ],
                "why": [
                    "Every triple of positions <code>i &lt; p &lt; q</code> is detected when the scan for <code>i</code> reaches <code>q</code>, because <code>nums[p]</code> is already in <code>seen</code>.",
                    "The sorted-tuple set removes repeats coming from equal values at different positions.",
                    "n outer steps, each an O(n) scan with O(1) set operations: <strong>O(n²)</strong> time. <code>seen</code> and <code>found</code> take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0 (−1): scanning 0, 1, 2, −1, −4. At x=1 the partner 0 is in seen: (−1, 0, 1).",
                        "Still i=0: at x=−1 the partner 2 is in seen: (−1, −1, 2).",
                        "i=1 (0): at x=−1 the partner 1 is in seen, giving (−1, 0, 1) again; the set ignores it.",
                        "Later i find nothing new. Normalised: <strong>[[-1, -1, 2], [-1, 0, 1]]</strong>.",
                    ],
                    [
                        "i=0: x=0 (seen empty), then x=0 finds partner 0: (0, 0, 0). The third 0 finds it again.",
                        "i=1: the second x=0 finds it once more.",
                        "found never grows past one tuple.",
                        "The answer is <strong>[[0, 0, 0]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>seen</code> reset for every <code>i</code>?",
                     "It must only hold values to the right of <code>i</code> that come before the current <code>x</code>. Carrying it over would allow positions before <code>i</code> and reuse elements."],
                    ["Why check before adding <code>x</code> to <code>seen</code>?",
                     "Adding first would let <code>x</code> pair with itself, for example claiming (2, −1, −1) from a single −1."],
                    ["Does slicing <code>nums[i + 1:]</code> change the complexity?",
                     "Each slice is an O(n) copy, the same order as the scan, so the total stays O(n²)."],
                ],
            },
            "Sort, fix one, two pointers, skip duplicates": {
                "idea": [
                    "Sort first. Then for each first number <code>nums[i]</code>, find pairs to its right summing to <code>-nums[i]</code> with the two-pointer Two Sum II technique.",
                    "Sorting also puts equal values side by side, so duplicate triples can be skipped by comparing with the neighbour, with no set needed.",
                ],
                "steps": [
                    "Sort <code>nums</code>. Loop <code>i</code> up to <code>len(nums) - 3</code>; stop entirely once <code>nums[i] &gt; 0</code>.",
                    "If <code>nums[i]</code> equals <code>nums[i - 1]</code>, skip it: it would produce the same triples.",
                    "Set <code>lo = i + 1</code>, <code>hi = len(nums) - 1</code> and compute <code>s = nums[i] + nums[lo] + nums[hi]</code>.",
                    "If <code>s &lt; 0</code>, move <code>lo</code> right; if <code>s &gt; 0</code>, move <code>hi</code> left.",
                    "If <code>s == 0</code>, record the triple, move both pointers, then keep moving <code>lo</code> while it repeats the previous value.",
                ],
                "why": [
                    "For a fixed <code>i</code> the inner loop is exactly Two Sum II on a sorted range, so it finds every pair that completes the triple.",
                    "Skipping equal first numbers and equal second numbers means each distinct triple is emitted once; the third number is then forced.",
                    "If <code>nums[i] &gt; 0</code>, all three numbers are positive, so no later <code>i</code> can work.",
                    "Sorting is O(n log n), then n inner scans of O(n): <strong>O(n²)</strong> time. Apart from the sort and the output, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Sorted: [−4, −1, −1, 0, 1, 2].",
                        "i=0 (−4): sums −3, −3, −2, −1, all too small; lo walks up to hi. Nothing.",
                        "i=1 (−1): lo=2, hi=5 gives 0, record [−1, −1, 2]. lo=3, hi=4 gives 0, record [−1, 0, 1].",
                        "i=2 (−1): same as nums[1], skipped. i=3 (0): 0 + 1 + 2 = 3 &gt; 0, hi moves and the pointers meet.",
                        "The answer is <strong>[[-1, -1, 2], [-1, 0, 1]]</strong>.",
                    ],
                    [
                        "Sorted: [0, 0, 0, 0]. i runs over 0 and 1 only.",
                        "i=0: lo=1, hi=3, s=0, record [0, 0, 0]. lo=2, hi=2, so the loop ends.",
                        "i=1: equal to nums[0], skipped.",
                        "The answer is <strong>[[0, 0, 0]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why only skip duplicates of <code>lo</code> and not of <code>hi</code>?",
                     "After a match, if <code>nums[lo]</code> is new, the matching <code>nums[hi]</code> is forced to a new value too, because the sum is fixed. A repeated <code>hi</code> just gives a sum that is too big and gets moved past normally."],
                    ["Why <code>nums[i] == nums[i - 1]</code> and not <code>nums[i] == nums[i + 1]</code>?",
                     "Comparing with the next element would skip the first −1 in [−1, −1, 2] and lose the triple that uses both −1s. Comparing with the previous one keeps the first copy, which sees all pairs to its right."],
                    ["Why is the <code>nums[i] &gt; 0</code> break safe?",
                     "The array is sorted, so <code>nums[lo]</code> and <code>nums[hi]</code> are at least <code>nums[i]</code>; three positive numbers cannot sum to 0."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ 4Sum
    "four-sum": {
        "examples": [
            {"call": "sorted(sorted(q) for q in four_sum([1, 0, -1, 0, -2, 2], 0))",
             "expect": "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]"},
            {"call": "sorted(sorted(q) for q in four_sum([2, 2, 2, 2, 2], 8))", "expect": "[[2, 2, 2, 2]]"},
        ],
        "approaches": {
            "Every quadruple": {
                "idea": [
                    "Try every choice of four positions and keep those whose values sum to the target.",
                    "Sort each hit into a tuple and collect them in a set, so the same values found at different positions count once.",
                ],
                "steps": [
                    "Loop <code>c</code> over <code>itertools.combinations(nums, 4)</code>.",
                    "Keep <code>c</code> if <code>sum(c) == target</code>.",
                    "Normalise each kept one with <code>tuple(sorted(c))</code> inside a set comprehension.",
                    "Return each tuple as a list.",
                ],
                "why": [
                    "Every possible quadruple is checked, and the canonical sorted tuple removes repeats, so the output is exactly the distinct answers.",
                    "There are n choose 4 quadruples: <strong>O(n⁴)</strong> time.",
                    "The set holds one tuple per distinct answer: <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "6 numbers give 15 quadruples.",
                        "Three sum to 0: (1, 0, −1, 0), (1, −1, −2, 2) and (0, 0, −2, 2).",
                        "Sorted: (−1, 0, 0, 1), (−2, −1, 1, 2), (−2, 0, 0, 2), all different.",
                        "The normalised answer is <strong>[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]</strong>.",
                    ],
                    [
                        "5 numbers give 5 quadruples, each (2, 2, 2, 2) summing to 8.",
                        "The set keeps a single copy.",
                        "The answer is <strong>[[2, 2, 2, 2]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is this marked for small inputs only?",
                     "With n = 200 there are about 6.5·10⁷ quadruples, each summed and sorted. That is far too slow next to the O(n³) method."],
                    ["Could the same answer be added twice?",
                     "It is generated many times when values repeat, as in the second example, but the set stores it once."],
                    ["Is the output order fixed?",
                     "No, it comes from a set. The worked examples sort the result so every approach can be compared."],
                ],
            },
            "Two fixed loops plus two pointers": {
                "idea": [
                    "Extend 3Sum by one level: sort, fix the first two numbers with two loops, and find the last two with two pointers.",
                    "Skip any first or second number equal to the previous choice at that level, so each distinct quadruple appears once.",
                ],
                "steps": [
                    "Sort <code>nums</code>. Loop <code>i</code> from 0 to <code>n - 4</code>, skipping <code>nums[i] == nums[i - 1]</code>.",
                    "Loop <code>j</code> from <code>i + 1</code> to <code>n - 3</code>, skipping when <code>j &gt; i + 1</code> and <code>nums[j] == nums[j - 1]</code>.",
                    "Set <code>lo = j + 1</code>, <code>hi = n - 1</code> and compute the four-number sum <code>s</code>.",
                    "If <code>s &lt; target</code> move <code>lo</code> right; if <code>s &gt; target</code> move <code>hi</code> left.",
                    "On a match, record it, move both pointers, and step <code>lo</code> past any repeats.",
                ],
                "why": [
                    "For fixed <code>i</code> and <code>j</code>, the pointer scan is Two Sum II on the sorted range after <code>j</code>, so it finds every completing pair.",
                    "The duplicate skips at each of the first three positions make every distinct quadruple come out exactly once.",
                    "Sorting is O(n log n); the two loops times an O(n) scan give <strong>O(n³)</strong> time. Beyond the sort and the output, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Sorted: [−2, −1, 0, 0, 1, 2].",
                        "i=0, j=1 (−2, −1): sums −1, −1, then 0 at lo=4, hi=5: record [−2, −1, 1, 2].",
                        "i=0, j=2 (−2, 0): lo=3, hi=5 sums to 0: record [−2, 0, 0, 2]. j=3 is a repeat 0, skipped.",
                        "i=1, j=2 (−1, 0): sum 1, hi=4, then 0: record [−1, 0, 0, 1]. i=2, j=3 (0, 0): sum 3, no match.",
                        "The answer is <strong>[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]</strong>.",
                    ],
                    [
                        "Sorted: [2, 2, 2, 2, 2].",
                        "i=0, j=1: lo=2, hi=4 gives 8, record [2, 2, 2, 2]. lo=3, hi=3 ends the scan.",
                        "j=2 repeats nums[1], skipped. i=1 repeats nums[0], skipped.",
                        "The answer is <strong>[[2, 2, 2, 2]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>j &gt; i + 1</code> in the skip test, not <code>j &gt; 0</code>?",
                     "The first <code>j</code> for each <code>i</code> must always run, even when it equals <code>nums[i]</code>; otherwise [2, 2, 2, 2] would never be found."],
                    ["Can I break early like 3Sum's <code>nums[i] &gt; 0</code>?",
                     "Not with that test: the target can be negative, so positive numbers can still be too small. Bounds such as <code>nums[i] * 4 &gt; target</code> work, as the k-Sum version does."],
                    ["Does integer overflow matter here?",
                     "Not in Python, whose integers are unbounded. In Java or C++ the four-number sum can overflow 32 bits and needs a 64-bit type."],
                ],
            },
            "General k-Sum recursion": {
                "idea": [
                    "k-Sum reduces to (k − 1)-Sum: fix the smallest number <code>nums[i]</code>, then solve (k − 1)-Sum for <code>target - nums[i]</code> on the elements after it.",
                    "The recursion bottoms out at k = 2, solved with two pointers. Quick range checks prune calls that cannot possibly reach the target.",
                ],
                "steps": [
                    "Sort <code>nums</code> and call <code>k_sum(0, 4, target)</code>.",
                    "In <code>k_sum(start, k, target)</code>, return <code>[]</code> if <code>start</code> is past the end, if <code>nums[start] * k &gt; target</code> (even the smallest values overshoot), or if <code>nums[-1] * k &lt; target</code> (even the largest fall short).",
                    "For k = 2, run two pointers from <code>start</code> to the end, skipping a <code>lo</code> equal to its predecessor.",
                    "For k &gt; 2, loop <code>i</code> from <code>start</code>, skip repeats of <code>nums[i]</code>, and prefix <code>nums[i]</code> to every answer of <code>k_sum(i + 1, k - 1, target - nums[i])</code>.",
                    "Collect and return all the lists.",
                ],
                "why": [
                    "Every distinct answer has a smallest element; the loop tries each distinct value as that element, and the recursion finds every distinct completion of it.",
                    "The pruning tests are safe because the values are sorted: k numbers from <code>start</code> onward lie between <code>nums[start] * k</code> and <code>nums[-1] * k</code>.",
                    "Each recursion level adds an O(n) loop and the base case is O(n): <strong>O(n<sup>k−1</sup>)</strong> time, which is O(n³) for 4Sum.",
                    "The recursion is only k deep: <strong>O(k)</strong> space beyond the sort and the output.",
                ],
                "dry": [
                    [
                        "Sorted [−2, −1, 0, 0, 1, 2]. k_sum(0, 4, 0) fixes −2 and calls k_sum(1, 3, 2).",
                        "That fixes −1: k_sum(2, 2, 3) returns [[1, 2]]. It fixes 0: k_sum(3, 2, 2) returns [[0, 2]]. The second 0 is skipped; 1 and 2 are pruned.",
                        "Back at the top it fixes −1: k_sum(2, 3, 1) fixes 0, and k_sum(3, 2, 1) returns [[0, 1]].",
                        "Fixing 0 at the top gives only pruned calls (e.g. 1 · 2 &gt; 0). Result: <strong>[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]</strong>.",
                    ],
                    [
                        "k_sum(0, 4, 8): 2·4 = 8 is neither &gt; 8 nor &lt; 8, so no pruning.",
                        "Fix 2: k_sum(1, 3, 6). Fix 2: k_sum(2, 2, 4) returns [[2, 2]].",
                        "Every later 2 at both levels is a repeat and is skipped.",
                        "The answer is <strong>[[2, 2, 2, 2]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the duplicate check <code>lo &gt; start</code> rather than <code>lo &gt; 0</code>?",
                     "The first element of the range must always be usable, even if it equals the element before <code>start</code> that the caller fixed. Otherwise [2, 2, 2, 2] would be missed."],
                    ["Are the pruning tests correct with negative numbers?",
                     "Yes. They only use the order of the sorted values: the smallest possible sum of k items is at least <code>nums[start] * k</code> and the largest at most <code>nums[-1] * k</code>, whatever the signs."],
                    ["Why bother with the general version for 4Sum?",
                     "It is the same O(n³) as the two loops, but it works for any k without new code, which interviewers like as a follow-up."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ rotate array
    "rotate-array": {
        "examples": [
            {"setup": "a = [1, 2, 3, 4, 5, 6, 7]\nrotate(a, 3)", "call": "a", "expect": "[5, 6, 7, 1, 2, 3, 4]"},
            {"setup": "a = [1, 2, 3, 4, 5, 6]\nrotate(a, 8)", "call": "a", "expect": "[5, 6, 1, 2, 3, 4]"},
        ],
        "approaches": {
            "Rotate by one, k times": {
                "idea": [
                    "Rotating right by k is the same as rotating right by 1, k times.",
                    "A rotation by 1 is easy in place: remember the last element, shift everything one step right, and put it at the front.",
                ],
                "steps": [
                    "Let <code>n = len(nums)</code>; repeat <code>k % n</code> times, since n rotations bring the array back.",
                    "Save <code>last = nums[-1]</code>.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 1, setting <code>nums[i] = nums[i - 1]</code>.",
                    "Write <code>nums[0] = last</code>.",
                ],
                "why": [
                    "Each pass moves every element one step right, wrapping the last to the front, so k passes move each element k steps.",
                    "The shift runs right to left so each value is copied before its slot is overwritten.",
                    "<code>k % n</code> passes of n moves: <strong>O(n · k)</strong> time. One saved value: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "k % 7 = 3 passes.",
                        "Pass 1: [7, 1, 2, 3, 4, 5, 6].",
                        "Pass 2: [6, 7, 1, 2, 3, 4, 5]. Pass 3: [5, 6, 7, 1, 2, 3, 4].",
                        "a is <strong>[5, 6, 7, 1, 2, 3, 4]</strong>.",
                    ],
                    [
                        "k = 8 but 8 % 6 = 2, so only two passes.",
                        "Pass 1: [6, 1, 2, 3, 4, 5].",
                        "Pass 2: [5, 6, 1, 2, 3, 4].",
                        "a is <strong>[5, 6, 1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why shift from the right end instead of the left?",
                     "Going left to right would copy <code>nums[0]</code> into every slot. Going right to left reads each value before it is overwritten."],
                    ["What does <code>k % n</code> buy?",
                     "Without it, k = 10⁹ would mean 10⁹ passes. Rotating by n is a no-op, so only the remainder matters."],
                    ["When is O(n · k) acceptable?",
                     "Only when k is tiny. In the worst case k ≈ n, which is quadratic."],
                ],
            },
            "Extra array": {
                "idea": [
                    "Element <code>i</code> ends up at index <code>(i + k) % n</code>: k steps right, wrapping around.",
                    "Place every element straight into its final slot in a new array, then copy that back.",
                ],
                "steps": [
                    "Create <code>out = [0] * n</code>.",
                    "For each <code>i, x</code>, set <code>out[(i + k) % n] = x</code>.",
                    "Copy back into the original list with <code>nums[:] = out</code>.",
                    "The modulo handles both the wrap-around and any <code>k &gt;= n</code>.",
                ],
                "why": [
                    "<code>i ↦ (i + k) % n</code> is a bijection on 0..n−1, so every slot of <code>out</code> is written exactly once with the right value.",
                    "Writing into a separate array means no value is overwritten before it is read.",
                    "One pass plus a copy: <strong>O(n)</strong> time. The new array is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 7, k = 3. 1→3, 2→4, 3→5, 4→6.",
                        "5→(4 + 3) % 7 = 0, 6→1, 7→2.",
                        "out = [5, 6, 7, 1, 2, 3, 4], copied into nums.",
                        "a is <strong>[5, 6, 7, 1, 2, 3, 4]</strong>.",
                    ],
                    [
                        "n = 6, k = 8, so (i + 8) % 6 = (i + 2) % 6.",
                        "1→2, 2→3, 3→4, 4→5, 5→0, 6→1.",
                        "out = [5, 6, 1, 2, 3, 4].",
                        "a is <strong>[5, 6, 1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>nums[:] = out</code> instead of <code>nums = out</code>?",
                     "The second only rebinds the local name; the caller's list stays unrotated. Slice assignment writes into the existing list."],
                    ["Can I write <code>nums[:] = nums[-k:] + nums[:-k]</code>?",
                     "Yes, after <code>k %= n</code>. Without the modulo, k ≥ n breaks it, and k = 0 needs care: <code>nums[-0:]</code> is the whole list, which happens to still give the right answer."],
                    ["Is there a way to avoid the extra array?",
                     "Yes: three reversals or cyclic replacements, both O(n) time and O(1) space."],
                ],
            },
            "Three reversals": {
                "idea": [
                    "Rotating right by k moves the last k elements to the front, keeping each block's internal order.",
                    "Reversing the whole array brings the last k to the front but backwards; reversing each block again restores its order.",
                ],
                "steps": [
                    "Reduce <code>k %= n</code>.",
                    "Define <code>rev(lo, hi)</code>, the in-place two-pointer reversal of <code>nums[lo..hi]</code>.",
                    "Call <code>rev(0, n - 1)</code> to reverse everything.",
                    "Call <code>rev(0, k - 1)</code> to fix the first k elements.",
                    "Call <code>rev(k, n - 1)</code> to fix the remaining n − k.",
                ],
                "why": [
                    "Write the array as A then B, where B is the last k elements. Reversing all gives rev(B) then rev(A); reversing each part gives B then A, the rotation.",
                    "Each element is swapped at most twice in total: <strong>O(n)</strong> time.",
                    "Only the swap indices are stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "k = 3. Reverse all: [7, 6, 5, 4, 3, 2, 1].",
                        "Reverse indices 0..2: [5, 6, 7, 4, 3, 2, 1].",
                        "Reverse indices 3..6: [5, 6, 7, 1, 2, 3, 4].",
                        "a is <strong>[5, 6, 7, 1, 2, 3, 4]</strong>.",
                    ],
                    [
                        "k = 8 % 6 = 2. Reverse all: [6, 5, 4, 3, 2, 1].",
                        "Reverse indices 0..1: [5, 6, 4, 3, 2, 1].",
                        "Reverse indices 2..5: [5, 6, 1, 2, 3, 4].",
                        "a is <strong>[5, 6, 1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["What breaks if I skip <code>k %= n</code>?",
                     "With k = 8 and n = 6, <code>rev(0, 7)</code> would index past the end and raise an IndexError."],
                    ["What about k = 0 after the modulo?",
                     "<code>rev(0, -1)</code> does nothing and <code>rev(0, n - 1)</code> undoes the first full reversal, so the array is unchanged, which is right."],
                    ["How do I rotate left instead?",
                     "Reverse the first k, then the rest, then the whole array; or rotate right by n − k."],
                ],
            },
            "Cyclic replacements": {
                "idea": [
                    "Pick up an element and put it where it belongs, <code>(i + k) % n</code>; that displaces another element, which you carry to its own target, and so on.",
                    "The chain eventually returns to where it started. If n and k share a factor, one chain does not cover everything, so start new chains until all n elements have moved.",
                ],
                "steps": [
                    "Reduce <code>k %= n</code> and set <code>moved = start = 0</code>.",
                    "While <code>moved &lt; n</code>: set <code>i = start</code> and <code>carry = nums[start]</code>.",
                    "Repeat: <code>j = (i + k) % n</code>; swap <code>carry</code> into <code>nums[j]</code>, taking the old <code>nums[j]</code> as the new carry; set <code>i = j</code> and count one more move.",
                    "Stop the chain when <code>i</code> is back at <code>start</code>.",
                    "Then try the next chain from <code>start + 1</code>.",
                ],
                "why": [
                    "Every element is written once, directly to its final index, so after n moves the array is rotated.",
                    "The chain from <code>start</code> visits exactly the indices congruent to <code>start</code> modulo gcd(n, k), so the first gcd(n, k) starts cover every index once and the chains never overlap.",
                    "n moves in total: <strong>O(n)</strong> time. One carried value and a few counters: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 7, k = 3, gcd 1: a single chain from index 0 does everything.",
                        "carry 1 → index 3 (picks up 4), 4 → 6 (picks up 7), 7 → 2 (picks up 3).",
                        "3 → 5, 6 → 1, 2 → 4, and 5 → 0, back at the start after 7 moves.",
                        "a is <strong>[5, 6, 7, 1, 2, 3, 4]</strong>.",
                    ],
                    [
                        "n = 6, k = 8 % 6 = 2, gcd 2: two chains of 3.",
                        "Chain 0: 1 → 2, 3 → 4, 5 → 0. moved = 3, back at 0: [5, 2, 1, 4, 3, 6].",
                        "Chain 1: 2 → 3, 4 → 5, 6 → 1. moved = 6.",
                        "a is <strong>[5, 6, 1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can't one chain always do it?",
                     "With n = 6 and k = 2, starting at 0 only visits 0, 2, 4. The odd indices form a separate cycle, so a second start is needed."],
                    ["Why is <code>start += 1</code> enough to find the next chain?",
                     "The cycles are the residue classes modulo gcd(n, k), and their smallest members are 0, 1, …, gcd − 1. Starts are tried in that order and <code>moved</code> stops the loop once all are done."],
                    ["Why count <code>moved</code> rather than compute gcd?",
                     "It avoids the number theory: the loop just stops after exactly n placements."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ container with most water
    "container-most-water": {
        "examples": [
            {"call": "max_area([1, 8, 6, 2, 5, 4, 8, 3, 7])", "expect": "49"},
            {"call": "max_area([4, 3, 2, 1, 4])", "expect": "16"},
        ],
        "approaches": {
            "Every pair": {
                "idea": [
                    "Any two lines <code>i &lt; j</code> form a container: width <code>j - i</code>, height <code>min(height[i], height[j])</code>, since water spills over the shorter line.",
                    "Compute that area for every pair and take the largest.",
                ],
                "steps": [
                    "Let <code>n = len(height)</code>.",
                    "Generate <code>(j - i) * min(height[i], height[j])</code> for every <code>i</code> and every <code>j &gt; i</code>.",
                    "Return the <code>max</code> of those areas.",
                    "The generator needs no list in memory; <code>max</code> consumes it as it goes.",
                ],
                "why": [
                    "Every possible container is one pair, and all pairs are measured, so the maximum is exact.",
                    "There are n(n − 1)/2 pairs: <strong>O(n²)</strong> time.",
                    "The generator produces one area at a time: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "There are 36 pairs.",
                        "Some samples: (0, 8) gives 8 · 1 = 8; (1, 6) gives 5 · 8 = 40.",
                        "(1, 8) gives 7 · min(8, 7) = 49, the largest.",
                        "It returns <strong>49</strong>.",
                    ],
                    [
                        "There are 10 pairs.",
                        "(0, 4) gives 4 · 4 = 16. Narrower pairs are capped by the short middle lines, e.g. (0, 1) gives 1 · 3 = 3.",
                        "It returns <strong>16</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>min</code> and not <code>max</code> of the two heights?",
                     "Water rises only to the shorter wall before it spills over."],
                    ["Do the lines between i and j matter?",
                     "No. They are thin lines, not walls, so they neither block nor reduce the water in this problem; that is the difference from Trapping Rain Water."],
                    ["What does it return for fewer than two lines?",
                     "<code>max</code> of an empty generator raises a ValueError. The problem guarantees n ≥ 2."],
                ],
            },
            "Two pointers, move the shorter side": {
                "idea": [
                    "Start with the widest container, the two outer lines. Every other container is narrower, so it can only win by being taller.",
                    "The shorter of the two lines limits the height. Keeping it and moving the other line in can only make the container narrower and no taller, so the shorter line is done: move it inward.",
                ],
                "steps": [
                    "Set <code>lo, hi = 0, len(height) - 1</code> and <code>best = 0</code>.",
                    "While <code>lo &lt; hi</code>, update <code>best</code> with <code>(hi - lo) * min(height[lo], height[hi])</code>.",
                    "If <code>height[lo] &lt; height[hi]</code>, move <code>lo</code> right.",
                    "Otherwise move <code>hi</code> left (this also handles ties).",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "Say <code>height[lo]</code> is shorter. Any container using <code>lo</code> with a line inside <code>hi</code> has smaller width and height at most <code>height[lo]</code>, so it cannot beat the area just measured. Discarding <code>lo</code> loses nothing.",
                    "Each step discards one line safely, so the best pair is measured before either of its lines is dropped.",
                    "The pointers close the gap by one per step: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0 (1), hi=8 (7): area 8 · 1 = 8. 1 is shorter, lo=1.",
                        "lo=1 (8), hi=8 (7): area 7 · 7 = 49, best = 49. 7 is shorter, hi=7.",
                        "hi=7 (3): 18. hi=6 (8): 40; a tie, so hi moves. hi=5..2 give 16, 15, 4, 6.",
                        "The pointers meet. It returns <strong>49</strong>.",
                    ],
                    [
                        "lo=0 (4), hi=4 (4): area 4 · 4 = 16. A tie, so hi moves.",
                        "hi=3 (1): 3. hi=2 (2): 4. hi=1 (3): 3.",
                        "The pointers meet with best still 16.",
                        "It returns <strong>16</strong>.",
                    ],
                ],
                "faq": [
                    ["What if the two heights are equal: which pointer should move?",
                     "Either. Any better container would need both lines taller than this height, so neither of the two equal lines can be in it; moving one of them is safe."],
                    ["Why not move the taller side?",
                     "That keeps the short line as the limit while the width shrinks, so the area can only fall; you could skip the true best pair."],
                    ["Does a taller line after the move always give a bigger area?",
                     "No, the width shrank. The point is only that the discarded line could never do better, so the search space shrinks safely."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ boats to save people
    "boats-to-save-people": {
        "examples": [
            {"call": "num_rescue_boats([3, 2, 2, 1], 3)", "expect": "3"},
            {"call": "num_rescue_boats([3, 5, 3, 4], 5)", "expect": "4"},
        ],
        "approaches": {
            "Sort, pair heaviest with lightest": {
                "idea": [
                    "A boat holds at most two people, so every boat is either one person or a pair under the limit.",
                    "The heaviest person needs a boat anyway. The best partner to give them is the lightest person: if even the lightest does not fit, nobody does.",
                ],
                "steps": [
                    "Sort <code>people</code>. Set <code>lo = 0</code>, <code>hi = len(people) - 1</code>, <code>boats = 0</code>.",
                    "While <code>lo &lt;= hi</code>: if <code>people[lo] + people[hi] &lt;= limit</code>, the lightest rides along, so <code>lo += 1</code>.",
                    "The heaviest always leaves: <code>hi -= 1</code>.",
                    "Count one boat per iteration.",
                    "Return <code>boats</code>.",
                ],
                "why": [
                    "Exchange argument: in any optimal plan, the heaviest person's partner can be swapped for the lightest person without breaking the limit, so pairing them is never worse.",
                    "If the lightest does not fit with the heaviest, the heaviest must go alone in every plan, which is what the code does.",
                    "Sorting is <strong>O(n log n)</strong> time and the scan O(n). The sorted copy is <strong>O(n)</strong> space (O(1) if you sort in place).",
                ],
                "dry": [
                    [
                        "Sorted: [1, 2, 2, 3].",
                        "lo=0 (1), hi=3 (3): 4 &gt; 3, so 3 goes alone. boats=1.",
                        "lo=0 (1), hi=2 (2): 3 ≤ 3, they share. boats=2, lo=1, hi=1.",
                        "lo=hi=1 (2): the last person goes alone. boats=3. It returns <strong>3</strong>.",
                    ],
                    [
                        "Sorted: [3, 3, 4, 5], limit 5.",
                        "5 + 3 &gt; 5: alone. 4 + 3 &gt; 5: alone.",
                        "3 + 3 &gt; 5: alone. Then the last 3 alone.",
                        "Nobody can share: <strong>4</strong> boats.",
                    ],
                ],
                "faq": [
                    ["Why <code>lo &lt;= hi</code> and not <code>lo &lt; hi</code>?",
                     "When <code>lo == hi</code> one person is left who still needs a boat. With <code>&lt;</code> that person would never be counted."],
                    ["Why not pair the two lightest together?",
                     "It wastes the light people, who are the only ones able to share with heavy ones. On [1, 1, 2, 2] with limit 3, pairing 1 + 1 leaves both 2s alone (3 boats), while the greedy pairs each 2 with a 1 (2 boats)."],
                    ["Does the greedy work if a boat can hold three people?",
                     "No, that version is a bin-packing problem; this proof relies on the two-person cap."],
                ],
            },
            "Counting sort, then the same greedy": {
                "idea": [
                    "Weights are integers between 1 and <code>limit</code>, so they can be sorted by counting instead of comparing.",
                    "Once sorted, run exactly the same heaviest-with-lightest greedy.",
                ],
                "steps": [
                    "Make <code>counts = [0] * (limit + 1)</code> and tally each weight.",
                    "Rebuild the sorted list <code>ordered</code> by emitting each weight <code>w</code> <code>counts[w]</code> times, smallest first.",
                    "Set <code>lo</code>, <code>hi</code> to the ends of <code>ordered</code> and <code>boats = 0</code>.",
                    "While <code>lo &lt;= hi</code>: move <code>lo</code> if the pair fits, always move <code>hi</code>, count a boat.",
                    "Return <code>boats</code>.",
                ],
                "why": [
                    "Counting sort yields the same sorted order, so the greedy and its exchange argument carry over unchanged.",
                    "Tallying is O(n), rebuilding is O(n + limit), the greedy is O(n): <strong>O(n + limit)</strong> time, which beats sorting when limit is small.",
                    "The count array is <strong>O(limit)</strong> space, plus O(n) for <code>ordered</code>.",
                ],
                "dry": [
                    [
                        "counts for weights 0..3 = [0, 1, 2, 1], so ordered = [1, 2, 2, 3].",
                        "3 + 1 &gt; 3: 3 alone. 2 + 1 ≤ 3: they share.",
                        "The last 2 goes alone.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "counts for weights 0..5 = [0, 0, 0, 2, 1, 1], so ordered = [3, 3, 4, 5].",
                        "Every pair exceeds 5, so each person gets a boat.",
                        "It returns <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["When is this better than a normal sort?",
                     "When <code>limit</code> is not much larger than n. The problem caps limit at 3·10⁴, so it is linear-ish in practice."],
                    ["What if a weight exceeded <code>limit</code>?",
                     "<code>counts[w]</code> would raise an IndexError. The problem guarantees every weight is at most limit, since otherwise that person could not be saved at all."],
                    ["Could I skip building <code>ordered</code> and walk the counts directly?",
                     "Yes, with two pointers over weight values and their counts. It saves O(n) memory but is fiddlier to get right."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ trapping rain water
    "trapping-rain-water": {
        "examples": [
            {"call": "trap([4, 2, 0, 3, 2, 5])", "expect": "9"},
            {"call": "trap([3, 0, 1, 0, 2])", "expect": "5"},
        ],
        "approaches": {
            "Scan left and right from every bar": {
                "idea": [
                    "Water above bar <code>i</code> rises to the lower of the tallest wall on its left and the tallest on its right; anything higher spills over that side.",
                    "So the water on bar <code>i</code> is <code>min(tallest left, tallest right) - height[i]</code>. Compute both maxima directly for every bar.",
                ],
                "steps": [
                    "Set <code>water = 0</code>.",
                    "For each index <code>i</code>, compute <code>left = max(height[:i + 1])</code> and <code>right = max(height[i:])</code>.",
                    "Both ranges include bar <code>i</code> itself, so neither max is below <code>height[i]</code>.",
                    "Add <code>min(left, right) - height[i]</code> to <code>water</code>; it is never negative.",
                    "Return <code>water</code>.",
                ],
                "why": [
                    "The column above bar <code>i</code> is held in by the highest wall on each side; the lower of the two sets the water level, so the formula is exact per bar, and the total is the sum.",
                    "Each bar scans the whole array for its two maxima: <strong>O(n²)</strong> time.",
                    "The slices <code>height[:i + 1]</code> and <code>height[i:]</code> are temporary copies, so this code uses O(n) scratch memory at a time; scanning with indices instead gives the listed <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Bar 0 (4): left 4, right 5, level 4, water 0.",
                        "Bar 1 (2): level min(4, 5) = 4, adds 2. Bar 2 (0): adds 4.",
                        "Bar 3 (3): adds 1. Bar 4 (2): adds 2. Bar 5 (5): adds 0.",
                        "Total 0 + 2 + 4 + 1 + 2 + 0 = <strong>9</strong>.",
                    ],
                    [
                        "Left maxima are all 3; right maxima are 3, 2, 2, 2, 2.",
                        "Levels: 3, 2, 2, 2, 2. The right wall (2) is the lower one for bars 1 to 4.",
                        "Water per bar: 0, 2, 1, 2, 0.",
                        "Total <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why include bar <code>i</code> in both maxima?",
                     "It guarantees <code>min(left, right) &gt;= height[i]</code>, so a bar taller than everything around it contributes 0 rather than a negative amount."],
                    ["Why the minimum of the two sides and not the maximum?",
                     "Water leaks out over the lower wall. Using the higher one would count water that cannot stay."],
                    ["Where does the repeated work come from?",
                     "Neighbouring bars recompute almost the same maxima. Storing them once in prefix and suffix arrays removes the inner scans."],
                ],
            },
            "Prefix and suffix maximum arrays": {
                "idea": [
                    "Same formula as the brute force, but compute every \"tallest to the left\" and \"tallest to the right\" once, in two passes.",
                    "<code>left[i]</code> is the running maximum from the left; <code>right[i]</code> is the running maximum from the right.",
                ],
                "steps": [
                    "Create <code>left</code> and <code>right</code> arrays of length n.",
                    "Left to right: <code>left[i] = max(height[i], left[i - 1])</code>, using 0 before index 0.",
                    "Right to left: <code>right[i] = max(height[i], right[i + 1])</code>, using 0 after the last index.",
                    "Sum <code>min(l, r) - h</code> over the three arrays zipped together.",
                ],
                "why": [
                    "<code>left[i]</code> equals <code>max(height[:i + 1])</code> by induction, and likewise for <code>right</code>, so each term matches the brute force exactly.",
                    "Three linear passes: <strong>O(n)</strong> time.",
                    "Two extra arrays of length n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "left = [4, 4, 4, 4, 4, 5].",
                        "right = [5, 5, 5, 5, 5, 5].",
                        "min(l, r) − h per bar: 0, 2, 4, 1, 2, 0.",
                        "Sum <strong>9</strong>.",
                    ],
                    [
                        "left = [3, 3, 3, 3, 3].",
                        "right = [3, 2, 2, 2, 2].",
                        "min(l, r) − h per bar: 0, 2, 1, 2, 0.",
                        "Sum <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the <code>if i else 0</code> guards?",
                     "Without them, <code>left[i - 1]</code> at <code>i = 0</code> would read <code>left[-1]</code>, the last element, which is 0 here only by luck of initialisation. The guard makes the boundary explicit."],
                    ["Could I drop one of the arrays?",
                     "Yes: build <code>right</code>, then walk left to right keeping the left maximum in a variable. The two-pointer version drops both."],
                    ["Does this handle an empty list?",
                     "Yes, all three passes do nothing and the sum is 0."],
                ],
            },
            "Monotonic stack, fill layer by layer": {
                "idea": [
                    "Instead of counting water per column, count it in horizontal layers: a layer forms when a bar is taller than the bar just before it and there is a wall further left.",
                    "Keep a stack of indices with non-increasing heights. When a taller bar arrives, each popped bar is the floor of a pond bounded by the new stack top on the left and the current bar on the right.",
                ],
                "steps": [
                    "Scan <code>i, h</code> over the bars with an empty <code>stack</code>.",
                    "While the stack top is shorter than <code>h</code>, pop it as <code>bottom</code>.",
                    "If the stack is now empty, there is no left wall: <code>break</code>.",
                    "Otherwise <code>left = stack[-1]</code>; the layer has <code>depth = min(height[left], h) - height[bottom]</code> and width <code>i - left - 1</code>. Add <code>depth * width</code>.",
                    "Push <code>i</code> and continue. Return <code>water</code>.",
                ],
                "why": [
                    "Each pop closes the pond above <code>bottom</code> up to the lower of its two walls, and bars between <code>left</code> and <code>i</code> have already been filled up to <code>height[bottom]</code>, so each layer is counted exactly once.",
                    "Each index is pushed once and popped at most once: <strong>O(n)</strong> time.",
                    "The stack can hold all n indices, for example on a falling staircase: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Push 0, 1, 2 (heights 4, 2, 0). i=3 (3): pop 2, left=1, depth 2 − 0 = 2, width 1: water 2.",
                        "Pop 1, left=0, depth 3 − 2 = 1, width 2: water 4. Push 3; stack = [0, 3].",
                        "Push 4. i=5 (5): pop 4, left=3, depth 1, width 1: water 5. Pop 3, left=0, depth 4 − 3 = 1, width 4: water 9.",
                        "Pop 0: no left wall, break. Push 5. It returns <strong>9</strong>.",
                    ],
                    [
                        "Push 0, 1 (heights 3, 0). i=2 (1): pop 1, left=0, depth 1, width 1: water 1. Push 2.",
                        "Push 3 (height 0); stack = [0, 2, 3].",
                        "i=4 (2): pop 3, left=2, depth 1, width 1: water 2. Pop 2, left=0, depth 2 − 1 = 1, width 3: water 5.",
                        "Height 3 is not shorter than 2, so the loop stops. It returns <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why use <code>min(height[left], h)</code> for the top of the layer?",
                     "Water in the pond can rise only to the lower of its two walls before spilling."],
                    ["Why subtract <code>height[bottom]</code> and not the original floor?",
                     "Lower layers were already counted when earlier bars were popped. This layer starts at the level of the bar just popped."],
                    ["Why <code>&lt;</code> and not <code>&lt;=</code> in the pop condition?",
                     "Either is correct. With equal heights, the pop gives depth 0 and adds nothing, so <code>&lt;</code> just avoids a pointless step."],
                ],
            },
            "Two pointers with running maxima": {
                "idea": [
                    "The water on a bar depends on the <em>smaller</em> of its two side maxima. You do not need the exact larger one, only to know it is larger.",
                    "Walk inward from both ends with <code>left_max</code> and <code>right_max</code>. Whichever side has the smaller running maximum is the one whose water level is already known for sure.",
                ],
                "steps": [
                    "Set <code>lo, hi</code> at the two ends and <code>left_max = right_max = water = 0</code>.",
                    "While <code>lo &lt; hi</code>, update <code>left_max</code> with <code>height[lo]</code> and <code>right_max</code> with <code>height[hi]</code>.",
                    "If <code>left_max &lt; right_max</code>, bar <code>lo</code> holds <code>left_max - height[lo]</code>; add it and move <code>lo</code> right.",
                    "Otherwise bar <code>hi</code> holds <code>right_max - height[hi]</code>; add it and move <code>hi</code> left.",
                    "Return <code>water</code>.",
                ],
                "why": [
                    "If <code>left_max &lt; right_max</code>, the true right maximum of bar <code>lo</code> is at least <code>right_max</code>, so the minimum of its two sides is exactly <code>left_max</code>. The mirror argument holds for <code>hi</code>.",
                    "Each step settles one bar with the same value the prefix/suffix formula would give.",
                    "One pass: <strong>O(n)</strong> time. A handful of variables: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0: left_max 4 &lt; right_max 5, adds 0, lo=1.",
                        "lo=1: adds 4 − 2 = 2. lo=2: adds 4. lo=3: adds 1. lo=4: adds 2.",
                        "The right side never moves because 5 stays the bigger maximum.",
                        "lo meets hi at 5. Total <strong>9</strong>.",
                    ],
                    [
                        "left_max 3, right_max 2: the right side is settled first. hi=4 adds 0.",
                        "hi=3 adds 2. hi=2 adds 2 − 1 = 1. hi=1 adds 2.",
                        "left_max stays 3 &gt; 2 the whole time, so only hi moves.",
                        "hi meets lo at 0. Total <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is it safe to use <code>left_max</code> without knowing the real right maximum of bar <code>lo</code>?",
                     "The real one is at least <code>right_max</code>, which is already bigger than <code>left_max</code>. The smaller side decides the level, so the exact value on the bigger side does not matter."],
                    ["Why update the maxima before adding water?",
                     "Including the current bar keeps <code>left_max - height[lo]</code> from going negative when the bar is a new maximum; it then just adds 0."],
                    ["Is the last bar where the pointers meet ever counted?",
                     "No, and it does not need to be: it is the tallest bar seen so far from both sides, so it holds no water."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ insert interval
    "insert-interval": {
        "examples": [
            {"call": "insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])",
             "expect": "[[1, 2], [3, 10], [12, 16]]"},
            {"call": "insert([[3, 5], [8, 9]], [1, 2])", "expect": "[[1, 2], [3, 5], [8, 9]]"},
        ],
        "approaches": {
            "Append, then Merge Intervals": {
                "idea": [
                    "Adding the new interval and merging overlaps is exactly the Merge Intervals problem on one more interval.",
                    "So reuse that solution: sort everything by start and extend the last merged group whenever the next interval overlaps it.",
                ],
                "steps": [
                    "Form <code>intervals + [new]</code> and sort it by start.",
                    "For each <code>s, e</code>: if <code>merged</code> is non-empty and <code>s &lt;= merged[-1][1]</code>, they overlap.",
                    "On overlap, extend: <code>merged[-1][1] = max(merged[-1][1], e)</code>.",
                    "Otherwise start a new group with <code>[s, e]</code>.",
                    "Return <code>merged</code>.",
                ],
                "why": [
                    "After sorting, any interval that overlaps the current group starts before the group ends, so one pass builds every group correctly.",
                    "Sorting costs <strong>O(n log n)</strong> time, even though only one interval was out of place.",
                    "The combined list and the output are <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Sorted: [1, 2], [3, 5], [4, 8], [6, 7], [8, 10], [12, 16].",
                        "[1, 2] starts a group. [3, 5]: 3 &gt; 2, new group.",
                        "[4, 8] extends it to [3, 8]; [6, 7] fits inside; [8, 10] touches and extends to [3, 10].",
                        "[12, 16] is new. Result <strong>[[1, 2], [3, 10], [12, 16]]</strong>.",
                    ],
                    [
                        "Sorted: [1, 2], [3, 5], [8, 9].",
                        "3 &gt; 2 and 8 &gt; 5, so nothing overlaps.",
                        "Each interval becomes its own group.",
                        "Result <strong>[[1, 2], [3, 5], [8, 9]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;=</code> in the overlap test?",
                     "Intervals that only touch, like [3, 8] and [8, 10], share the point 8 and must be merged."],
                    ["Why <code>max</code> when extending?",
                     "A later interval can sit fully inside the group, like [6, 7] inside [3, 8]; plain assignment would shrink the group."],
                    ["Why is this not the intended answer?",
                     "The input is already sorted and non-overlapping, so one linear scan suffices. Sorting again wastes the log factor."],
                ],
            },
            "Three-phase linear scan": {
                "idea": [
                    "Because the intervals are sorted and disjoint, they fall into three consecutive blocks: those entirely before the new one, those overlapping it, and those entirely after.",
                    "Copy the first block, fold the middle block into the new interval, then copy the last block.",
                ],
                "steps": [
                    "Set <code>i = 0</code> and <code>start, end = new</code>.",
                    "Phase 1: while <code>intervals[i][1] &lt; start</code>, the interval ends before the new one begins; append it.",
                    "Phase 2: while <code>intervals[i][0] &lt;= end</code>, it overlaps; widen <code>start</code> to the min and <code>end</code> to the max.",
                    "Append the merged <code>[start, end]</code>.",
                    "Phase 3: return <code>out + intervals[i:]</code>, the untouched rest.",
                ],
                "why": [
                    "Phase 1 stops at the first interval reaching <code>start</code>; since the list is sorted, all earlier ones lie fully to the left.",
                    "Phase 2 absorbs every interval that starts no later than the growing <code>end</code>; the first that starts later, and all after it, lie fully to the right.",
                    "Each interval is visited once: <strong>O(n)</strong> time. The output list is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Phase 1: [1, 2] ends at 2 &lt; 4, copied. [3, 5] ends at 5, stop.",
                        "Phase 2: [3, 5] gives [3, 8]. [6, 7] stays [3, 8]. [8, 10]: 8 ≤ 8, gives [3, 10].",
                        "[12, 16]: 12 &gt; 10, stop. Append [3, 10].",
                        "Phase 3 adds [12, 16]: <strong>[[1, 2], [3, 10], [12, 16]]</strong>.",
                    ],
                    [
                        "Phase 1: [3, 5] ends at 5, not before 1, so nothing is copied.",
                        "Phase 2: [3, 5] starts at 3 &gt; 2, so nothing overlaps.",
                        "Append [1, 2] as it is.",
                        "Phase 3 adds the rest: <strong>[[1, 2], [3, 5], [8, 9]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;</code> in phase 1 but <code>&lt;=</code> in phase 2?",
                     "An interval ending exactly at <code>start</code> touches the new one and must merge, so it must fail the phase 1 test and pass the phase 2 test."],
                    ["Does <code>start</code> really need <code>min</code> on every overlapping interval?",
                     "No. Only the first overlapping interval can start before <code>start</code>, since the list is sorted; applying <code>min</code> every time is just simpler and harmless."],
                    ["What if <code>intervals</code> is empty?",
                     "Both loops are skipped, <code>[start, end]</code> is appended, and the answer is just the new interval."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge intervals
    "merge-intervals": {
        "examples": [
            {"call": "merge([[1, 3], [8, 10], [2, 6], [9, 9], [15, 18]])", "expect": "[[1, 6], [8, 10], [15, 18]]"},
            {"call": "merge([[2, 3], [1, 10], [10, 12]])", "expect": "[[1, 12]]"},
        ],
        "approaches": {
            "Overlap graph, connected components": {
                "idea": [
                    "Treat each interval as a node and join two nodes when the intervals overlap.",
                    "A merged interval is a connected component: overlaps chain together, and the component covers from its smallest start to its largest end.",
                ],
                "steps": [
                    "Build <code>adj[i]</code>: every <code>j != i</code> with <code>intervals[i][0] &lt;= intervals[j][1]</code> and <code>intervals[j][0] &lt;= intervals[i][1]</code>.",
                    "For each unseen <code>i</code>, run a stack-based DFS, marking nodes in <code>seen</code> when pushed.",
                    "While exploring, keep <code>lo</code> as the min start and <code>hi</code> as the max end of the component.",
                    "Append <code>[lo, hi]</code> when the stack empties.",
                    "Return the components sorted by start.",
                ],
                "why": [
                    "Two intervals end up in one merged block exactly when a chain of overlaps links them, which is the definition of a connected component.",
                    "Building the adjacency lists compares every pair: <strong>O(n²)</strong> time, and the lists can hold n² edges: <strong>O(n²)</strong> space.",
                    "The DFS itself is linear in nodes plus edges, so it does not change those bounds.",
                ],
                "dry": [
                    [
                        "adj: 0–2 ([1, 3] and [2, 6]) and 1–3 ([8, 10] and [9, 9]); 4 has no edges.",
                        "DFS from 0 visits 0, 2: [1, 6].",
                        "DFS from 1 visits 1, 3: [8, 10]. DFS from 4: [15, 18].",
                        "Sorted: <strong>[[1, 6], [8, 10], [15, 18]]</strong>.",
                    ],
                    [
                        "adj: 0–1 ([2, 3] inside [1, 10]) and 1–2 ([1, 10] touches [10, 12]). 0 and 2 do not overlap.",
                        "DFS from 0 reaches 1, then 2 through it.",
                        "lo = 1, hi = 12.",
                        "Result <strong>[[1, 12]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the overlap test <code>a.start &lt;= b.end and b.start &lt;= a.end</code>?",
                     "Two intervals are disjoint only when one ends before the other starts. Negating that gives this test, and it covers containment and touching too."],
                    ["Why can't I just merge each interval with its direct neighbours?",
                     "In the second example [2, 3] and [10, 12] do not overlap, yet both belong with [1, 10]. Only the transitive closure, the component, gets that right."],
                    ["Why show a quadratic method at all?",
                     "It states the problem precisely as a graph question. Sorting then exploits the 1-D structure to find the same components in one pass."],
                ],
            },
            "Sort by start, extend the last group": {
                "idea": [
                    "Once intervals are sorted by start, every interval that belongs to the current group comes right after it in the list.",
                    "So scan in order: either the next interval overlaps the last group and extends it, or it starts a new group.",
                ],
                "steps": [
                    "Sort the intervals; Python sorts lists by first element, then second.",
                    "For each <code>s, e</code>: if <code>out</code> is non-empty and <code>s &lt;= out[-1][1]</code>, it overlaps the last group.",
                    "On overlap, set <code>out[-1][1] = max(out[-1][1], e)</code>; the interval may be fully contained.",
                    "Otherwise append a fresh <code>[s, e]</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "If an interval starts after the current group's end, every later one starts even later, so the group can never grow again and is final.",
                    "Each overlapping interval only ever needs to extend the group's end, because its start is no smaller than the group's start.",
                    "Sorting is <strong>O(n log n)</strong> time; the scan is O(n). The sorted copy and output take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Sorted: [1, 3], [2, 6], [8, 10], [9, 9], [15, 18].",
                        "[1, 3] starts a group; [2, 6]: 2 ≤ 3, extends to [1, 6].",
                        "[8, 10] is new; [9, 9]: 9 ≤ 10, max(10, 9) keeps [8, 10].",
                        "[15, 18] is new. Result <strong>[[1, 6], [8, 10], [15, 18]]</strong>.",
                    ],
                    [
                        "Sorted: [1, 10], [2, 3], [10, 12].",
                        "[2, 3] is inside, so max keeps the end at 10.",
                        "[10, 12]: 10 ≤ 10 touches, end becomes 12.",
                        "Result <strong>[[1, 12]]</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong if I write <code>out[-1][1] = e</code>?",
                     "Contained intervals would shrink the group: [1, 10] followed by [2, 3] would become [1, 3] and lose [10, 12]'s overlap."],
                    ["Why <code>&lt;=</code> and not <code>&lt;</code>?",
                     "The problem counts touching intervals like [1, 4] and [4, 5] as overlapping, so they must merge into [1, 5]."],
                    ["Does appending <code>[s, e]</code> rather than the original list matter?",
                     "Yes: it makes a new list, so extending <code>out[-1][1]</code> never changes the caller's input intervals."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ non-overlapping intervals
    "non-overlapping-intervals": {
        "examples": [
            {"call": "erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]])", "expect": "1"},
            {"call": "erase_overlap_intervals([[1, 2], [1, 2], [1, 2]])", "expect": "2"},
        ],
        "approaches": {
            "DP: longest chain of compatible intervals": {
                "idea": [
                    "Removing the fewest intervals is the same as keeping the most intervals that do not overlap.",
                    "Sort by start; then <code>keep[i]</code>, the longest non-overlapping chain ending with interval <code>i</code>, is one more than the best chain ending at any earlier interval that finishes by the time <code>i</code> starts.",
                ],
                "steps": [
                    "Sort into <code>iv</code> and set <code>keep = [1] * n</code>: each interval alone is a chain.",
                    "For each <code>i</code>, loop over every earlier <code>j</code>.",
                    "If <code>iv[j][1] &lt;= iv[i][0]</code>, interval <code>j</code> can come just before <code>i</code>: <code>keep[i] = max(keep[i], keep[j] + 1)</code>.",
                    "The longest chain is <code>max(keep)</code>.",
                    "Return <code>len(iv) - max(keep)</code>.",
                ],
                "why": [
                    "Any non-overlapping set, listed by start, is a chain in which each interval ends by the next one's start, so the DP considers every possible predecessor.",
                    "Two nested loops over n intervals: <strong>O(n²)</strong> time.",
                    "The <code>keep</code> array: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "iv = [[1, 2], [1, 3], [2, 3], [3, 4]].",
                        "keep[0] = 1, keep[1] = 1 (nothing ends by 1).",
                        "keep[2] = 2 via [1, 2]. keep[3] = 3 via [2, 3].",
                        "max is 3, so 4 − 3 = <strong>1</strong>.",
                    ],
                    [
                        "iv = [[1, 2], [1, 2], [1, 2]].",
                        "No interval ends by 1, so every keep stays 1.",
                        "max is 1.",
                        "3 − 1 = <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;=</code> between the end of <code>j</code> and the start of <code>i</code>?",
                     "In this problem intervals that only touch, like [1, 2] and [2, 3], do not overlap, so they may both be kept."],
                    ["Why sort first?",
                     "So that every possible predecessor of <code>i</code> appears before it, which makes a single left-to-right DP pass enough."],
                    ["Why is the greedy preferred?",
                     "It finds the same maximum chain in O(n log n). The DP is still worth knowing, because it extends to weighted intervals, where greedy fails."],
                ],
            },
            "Greedy: sort by end, keep the earliest-ending": {
                "idea": [
                    "To fit as many intervals as possible, always keep the interval that frees up the line soonest: the one that ends first.",
                    "Sort by end, keep each interval that starts at or after the last kept end, and count the rest as removed.",
                ],
                "steps": [
                    "Set <code>removed = 0</code> and <code>end = -inf</code>.",
                    "Loop <code>s, e</code> over the intervals sorted by end.",
                    "If <code>s &gt;= end</code>, it fits after the last kept interval: keep it and set <code>end = e</code>.",
                    "Otherwise it overlaps the kept one: <code>removed += 1</code>.",
                    "Return <code>removed</code>.",
                ],
                "why": [
                    "Exchange argument: an optimal solution's first interval can be swapped for the earliest-ending one without causing any overlap, and repeating this shows greedy keeps as many as optimal.",
                    "Sorting is <strong>O(n log n)</strong> time; the scan is O(n).",
                    "Two variables beyond the sorted list: <strong>O(1)</strong> space beyond sorting.",
                ],
                "dry": [
                    [
                        "Sorted by end: [1, 2], [2, 3], [1, 3], [3, 4].",
                        "Keep [1, 2], end = 2. Keep [2, 3], end = 3.",
                        "[1, 3] starts at 1 &lt; 3: removed = 1. Keep [3, 4].",
                        "It returns <strong>1</strong>.",
                    ],
                    [
                        "All three are [1, 2].",
                        "Keep the first, end = 2.",
                        "The other two start at 1 &lt; 2: removed twice.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort by end and not by start?",
                     "Sorting by start and keeping greedily would keep [1, 100] before [2, 3] and [4, 5], blocking both. The earliest end leaves the most room."],
                    ["Why start <code>end</code> at minus infinity?",
                     "So the first interval is always kept, whatever its start, including negative starts."],
                    ["Why <code>s &gt;= end</code> and not <code>s &gt; end</code>?",
                     "Touching intervals are allowed together here. With <code>&gt;</code>, [1, 2] and [2, 3] would wrongly count as a removal."],
                ],
            },
            "Greedy by start, drop the longer-ending one": {
                "idea": [
                    "Sort by start and walk through the intervals. When two overlap, one has to go, and the one to keep is whichever ends first.",
                    "Track <code>end</code>, the end of the last interval kept; on an overlap shrink it to the smaller end, which models dropping the longer one.",
                ],
                "steps": [
                    "Sort into <code>iv</code>; set <code>removed = 0</code> and <code>end = iv[0][1]</code>.",
                    "Loop <code>s, e</code> over <code>iv[1:]</code>.",
                    "If <code>s &lt; end</code>, it overlaps: <code>removed += 1</code> and <code>end = min(end, e)</code>.",
                    "Otherwise no overlap: set <code>end = e</code>.",
                    "Return <code>removed</code>.",
                ],
                "why": [
                    "Of two overlapping intervals, keeping the one ending earlier is never worse, by the same exchange argument as the sort-by-end greedy.",
                    "Every later interval starts at or after the current start, so only <code>end</code> matters for future overlaps.",
                    "Sorting is <strong>O(n log n)</strong> time; then a single pass. <strong>O(1)</strong> space beyond sorting.",
                ],
                "dry": [
                    [
                        "Sorted: [1, 2], [1, 3], [2, 3], [3, 4]. end = 2.",
                        "[1, 3]: 1 &lt; 2, removed = 1, end = min(2, 3) = 2.",
                        "[2, 3]: no overlap, end = 3. [3, 4]: no overlap, end = 4.",
                        "It returns <strong>1</strong>.",
                    ],
                    [
                        "Sorted: three copies of [1, 2]. end = 2.",
                        "Second [1, 2]: 1 &lt; 2, removed = 1, end stays 2.",
                        "Third [1, 2]: removed = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>min(end, e)</code> on an overlap?",
                     "It keeps whichever of the two overlapping intervals ends first, leaving more room for the rest."],
                    ["What happens on an empty list?",
                     "<code>iv[0]</code> raises an IndexError. The problem guarantees at least one interval; otherwise return 0 first."],
                    ["Is this the same algorithm as the sort-by-end greedy?",
                     "It keeps the same number of intervals, just found in start order. Both are O(n log n)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ meeting rooms III
    "meeting-rooms-iii": {
        "examples": [
            {"call": "most_booked(2, [[0, 10], [1, 5], [2, 7], [3, 4]])", "expect": "0"},
            {"call": "most_booked(3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]])", "expect": "1"},
        ],
        "approaches": {
            "Simulate by scanning all rooms": {
                "idea": [
                    "Process meetings in start order and follow the rules literally: take the lowest-numbered free room, or if none is free, wait for the room that frees up first.",
                    "A delayed meeting keeps its length, so its new end is the room's free time plus the duration.",
                ],
                "steps": [
                    "Keep <code>free_at[r]</code>, when room <code>r</code> is next free, and <code>count[r]</code>.",
                    "For each <code>start, end</code> in sorted order, find the lowest <code>r</code> with <code>free_at[r] &lt;= start</code>.",
                    "If none, pick <code>room = min(range(n), key=lambda r: (free_at[r], r))</code>, the earliest-free room with ties to the lowest number, and shift <code>end</code> by <code>free_at[room] - start</code>.",
                    "Set <code>free_at[room] = end</code> and add one to <code>count[room]</code>.",
                    "Return <code>count.index(max(count))</code>, the lowest room with the top count.",
                ],
                "why": [
                    "Each step does exactly what the rules say, and start times are distinct, so processing in start order is the order meetings claim rooms.",
                    "Delays push meetings later but preserve their order, because a delayed meeting is still assigned before any later-starting one.",
                    "Sorting is O(m log m) and each meeting scans n rooms: <strong>O(m log m + m · n)</strong> time, with <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "[0, 10] → room 0. free_at = [10, 0].",
                        "[1, 5] → room 1. free_at = [10, 5].",
                        "[2, 7]: no room free; room 1 frees at 5, so it runs 5 to 10. [3, 4]: none free; both free at 10, room 0 wins the tie, runs 10 to 11.",
                        "count = [2, 2]. The lowest index with 2 is <strong>0</strong>.",
                    ],
                    [
                        "[1, 20] → room 0, [2, 10] → room 1, [3, 5] → room 2.",
                        "[4, 9]: none free; room 2 frees first at 5, runs 5 to 10. free_at = [20, 10, 10].",
                        "[6, 8]: none free; rooms 1 and 2 both free at 10, room 1 wins, runs 10 to 12.",
                        "count = [1, 2, 2], so the answer is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort by start time?",
                     "The rules hand out rooms in order of original start time, and delayed meetings keep that order."],
                    ["Why the key <code>(free_at[r], r)</code>?",
                     "When several rooms free up at the same moment, the rules give the meeting the lowest-numbered one, and the tuple's second part breaks that tie."],
                    ["Why <code>count.index(max(count))</code>?",
                     "<code>index</code> returns the first position with the max value, which is the lowest-numbered room, as the tie rule demands."],
                ],
            },
            "Two heaps: free rooms and busy rooms": {
                "idea": [
                    "Both decisions are \"smallest something\" queries: the lowest free room number, and the busy room that frees earliest (ties to the lowest number).",
                    "Keep a min-heap <code>free</code> of room numbers and a min-heap <code>busy</code> of <code>(end, room)</code> pairs.",
                ],
                "steps": [
                    "Start with <code>free = [0, 1, ..., n-1]</code>, already a valid heap, and empty <code>busy</code>.",
                    "For each meeting in start order, pop every busy room with <code>end &lt;= start</code> and push its number back onto <code>free</code>.",
                    "If <code>free</code> is non-empty, pop the lowest room and push <code>(end, room)</code> onto <code>busy</code>.",
                    "Otherwise pop the earliest <code>(finish, room)</code> and push <code>(finish + end - start, room)</code>: the delayed meeting keeps its length.",
                    "Count the room; finally return <code>count.index(max(count))</code>.",
                ],
                "why": [
                    "Releasing rooms that ended by <code>start</code> makes <code>free</code> exactly the rooms available now; tuple ordering in <code>busy</code> gives the earliest end, then the lowest room.",
                    "Each meeting does O(1) heap pushes and pops plus releases, and each room release matches an earlier push: <strong>O(m log m + m log n)</strong> time.",
                    "Both heaps together hold each room once: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "[0, 10]: room 0, busy = [(10, 0)]. [1, 5]: room 1, busy = [(5, 1), (10, 0)].",
                        "[2, 7]: free is empty; pop (5, 1), push (5 + 5, 1) = (10, 1).",
                        "[3, 4]: pop (10, 0), the tie goes to room 0; push (11, 0).",
                        "count = [2, 2]: <strong>0</strong>.",
                    ],
                    [
                        "Rooms 0, 1, 2 take [1, 20], [2, 10], [3, 5]. busy = [(5, 2), (10, 1), (20, 0)].",
                        "[4, 9]: nothing ends by 4; pop (5, 2), push (10, 2).",
                        "[6, 8]: nothing ends by 6; pop (10, 1) before (10, 2), push (12, 1).",
                        "count = [1, 2, 2]: <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why release with <code>&lt;=</code> and not <code>&lt;</code>?",
                     "Meetings are half-open: a room whose meeting ends at time t is free for one starting at t."],
                    ["Why store <code>(end, room)</code> rather than <code>(room, end)</code>?",
                     "The heap orders by the first item. We want the earliest end first, with the room number only breaking ties."],
                    ["Can the delayed end overflow in other languages?",
                     "Yes: repeated delays can push ends past 2³¹, so Java or C++ need 64-bit integers. Python's integers do not overflow."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum interval to include each query
    "min-interval-each-query": {
        "examples": [
            {"call": "min_interval([[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5])", "expect": "[3, 3, 1, 4]"},
            {"call": "min_interval([[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22])", "expect": "[2, -1, 4, 6]"},
        ],
        "approaches": {
            "Check every interval per query": {
                "idea": [
                    "For each query, look at every interval, keep the ones that contain it, and take the smallest size.",
                    "An interval <code>[l, r]</code> has size <code>r - l + 1</code>, because both ends count.",
                ],
                "steps": [
                    "Loop over each query <code>q</code> in its original order.",
                    "Collect <code>sizes</code> of every interval with <code>l &lt;= q &lt;= r</code>.",
                    "Append <code>min(sizes)</code>, or <code>-1</code> if no interval contains <code>q</code>.",
                    "Return the list of answers.",
                ],
                "why": [
                    "Each query sees every interval, so the minimum is exact.",
                    "n intervals per query, q queries: <strong>O(n · q)</strong> time.",
                    "The <code>sizes</code> list as written can hold up to n values per query; using <code>min</code> with a generator and <code>default=-1</code> would make it <strong>O(1)</strong> extra space beyond the output.",
                ],
                "dry": [
                    [
                        "q=2: [1, 4] (4) and [2, 4] (3) contain it: 3.",
                        "q=3: sizes 4, 3, 4: 3.",
                        "q=4: all four contain it, and [4, 4] has size 1: 1. q=5: only [3, 6] (4): 4.",
                        "Answer <strong>[3, 3, 1, 4]</strong>.",
                    ],
                    [
                        "q=2: sizes 2, 4, 8: 2. q=19: nothing contains it: −1.",
                        "q=5: [2, 5] (4) and [1, 8] (8): 4.",
                        "q=22: [20, 25] (6): 6.",
                        "Answer <strong>[2, -1, 4, 6]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>r - l + 1</code> and not <code>r - l</code>?",
                     "The problem counts integers in the closed range, so [4, 4] has size 1, not 0."],
                    ["Why check <code>if sizes</code> before calling <code>min</code>?",
                     "<code>min</code> of an empty list raises a ValueError; an empty list means the answer is −1."],
                    ["How slow is this in the worst case?",
                     "With 10⁵ intervals and 10⁵ queries it is 10¹⁰ checks, which is why the offline sweep exists."],
                ],
            },
            "Offline sweep with a min-heap": {
                "idea": [
                    "Answer the queries in increasing order rather than input order (\"offline\"), remembering each query's original position.",
                    "As the query value grows, add every interval that has started; drop from the heap any interval that has already ended. The smallest live interval is then the heap top.",
                ],
                "steps": [
                    "Sort <code>intervals</code> by start, and sort the queries as <code>(q, pos)</code> pairs. Start <code>out</code> as all −1.",
                    "For each <code>q</code>, push every interval with <code>l &lt;= q</code> as <code>(r - l + 1, r)</code>, advancing <code>i</code>.",
                    "Pop from the top while <code>heap[0][1] &lt; q</code>: that interval ended before <code>q</code> and will not contain any later query either.",
                    "If the heap is non-empty, <code>out[pos] = heap[0][0]</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "Every interval in the heap started at or before <code>q</code>. After the pops, the top also ends at or after <code>q</code>, so it contains <code>q</code> and is the smallest such one.",
                    "Stale intervals deeper in the heap are harmless until they reach the top; since queries only grow, anything that ended stays useless and can be popped for good.",
                    "Sorting is O(n log n + q log q); each interval is pushed and popped once, O(n log n): <strong>O(n log n + q log q)</strong> time, <strong>O(n + q)</strong> space.",
                ],
                "dry": [
                    [
                        "q=2: push [1, 4] as (4, 4) and [2, 4] as (3, 4). Top (3, 4): out[0] = 3.",
                        "q=3: push (4, 6). Top is still (3, 4): out[1] = 3.",
                        "q=4: push (1, 4). Top (1, 4): out[2] = 1.",
                        "q=5: pop (1, 4), (3, 4), (4, 4), all ending at 4. Top (4, 6): out[3] = 4. Answer <strong>[3, 3, 1, 4]</strong>.",
                    ],
                    [
                        "Sorted queries: 2, 5, 19, 22. q=2: push (8, 8), (2, 3), (4, 5). Top (2, 3): out[0] = 2.",
                        "q=5: pop (2, 3). Top (4, 5): out[2] = 4.",
                        "q=19: pop (4, 5) and (8, 8); the heap is empty, so out[1] stays −1.",
                        "q=22: push (6, 25): out[3] = 6. Answer <strong>[2, -1, 4, 6]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort the queries? The answer must be in the original order.",
                     "Sorting lets intervals enter and leave the heap only once. The saved <code>pos</code> puts each answer back in its original slot."],
                    ["Why only pop expired intervals from the top, not all of them?",
                     "Only the top is reported. An expired interval buried below a live one cannot affect the answer, and it will be popped once it reaches the top."],
                    ["Why store <code>r</code> in the heap entry?",
                     "The size alone cannot tell whether the interval still covers <code>q</code>; the end point is needed for the expiry check."],
                ],
            },
        },
    },
}
