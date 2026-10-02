# -*- coding: utf-8 -*-
"""Graphs topic (NeetCode 250: Graphs + Advanced Graphs). The union-find
problems from those lists (261, 323, 684, 721, 2709) are in the Union Find
topic. Same build contract as content/dsa.py."""

from graphs_basic import SECTION_TRAVERSAL, SECTION_TOPO
from graphs_adv import SECTION_WEIGHTED, SECTION_STRUCTURE

PRELUDE_GRAPHS = '''import bisect
import heapq
import itertools
import math
import random
from collections import Counter, defaultdict, deque
from functools import cache
'''

GRAPHS_TOPIC = dict(
    id="graphs",
    title="Graphs",
    prelude=PRELUDE_GRAPHS,
    sections=[SECTION_TRAVERSAL, SECTION_TOPO, SECTION_WEIGHTED, SECTION_STRUCTURE],
)
