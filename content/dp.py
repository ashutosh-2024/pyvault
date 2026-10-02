# -*- coding: utf-8 -*-
"""Dynamic programming topic for the DSA path.

Same contract as content/dsa.py: every `code` block is executed by build.py
with PRELUDE + this topic's `prelude` + the problem's `tests` appended.

Unlike the other topics, DP is organised into *patterns*. The topic page lists
the patterns; each pattern page opens with `idea` (what the state is and why
the recurrence has the shape it has) and then its problems. `summary` is the
one-liner shown on the pattern's box. Each pattern lives in its own module.

Problems with a `slug` get their statement, examples, constraints and tags
from content/leetcode.json. The GeeksforGeeks classics supply their own and
carry a `ref` link instead of a LeetCode one.

The ladder
----------
Every DP problem is written as the same progression, and the problem page
renders it in this order:

  approaches[0]  plain recursion (the brute force the recurrence comes from)
  recurrence     state, how to derive it, the relation with base cases
  approaches[1:] top-down memo, bottom-up table, two rows, one row (or two
                 variables for a 1-D state) - each with `change`, one line on
                 what changed from the step before and why it is safe - then
                 any approach beyond DP (greedy, math, bisect)

Extra keys used by DP problems:
  recurrence:  dict(state, derive[], formula, notes[]?)
  change:      on an approach, the "what changed" line
  small:       on an approach too slow for `tests` (exponential recursion);
               it is checked against the problem's `small_tests` instead
  `why` lists are rendered as bullet points, so keep each item to one idea.
"""

from dp_linear import FOUNDATIONS, LINEAR
from dp_knapsack import KNAPSACK
from dp_grid import GRID
from dp_lis import LIS
from dp_strings import TWO_STRINGS
from dp_interval import INTERVAL

PRELUDE_DP = '''import bisect
import itertools
import random
from functools import cache
from math import comb, inf, isqrt
'''


DP_TOPIC = dict(
    id="dp",
    title="Dynamic Programming",
    prelude=PRELUDE_DP,
    layout="patterns",
    sections=[FOUNDATIONS, LINEAR, KNAPSACK, GRID, LIS, TWO_STRINGS, INTERVAL],
)
