"""A binary heap that records its own sift steps, for heap animations.

    h = TracedHeap(kind="min", label="min-heap")
    for ev in h.push(5):         # each event: dict(tree=..., text=...)
        ...
    h.tree(marks={0: "answer"})  # snapshot as a viz tree

The layout is the standard array heap (children of i are 2i+1 and 2i+2), the
same one heapq uses, so the array row and the tree always agree.
"""
from ._kit import fmt


class TracedHeap:
    def __init__(self, kind="min", label=None, key=None, show=None):
        assert kind in ("min", "max")
        self.kind = kind
        self.a = []
        self.key = key or (lambda x: x)
        self.show = show or fmt
        self.label = label or f"{kind}-heap"

    # -- ordering
    def _better(self, x, y):
        kx, ky = self.key(x), self.key(y)
        return kx < ky if self.kind == "min" else kx > ky

    def __len__(self):
        return len(self.a)

    def top(self):
        return self.a[0]

    # -- snapshots
    def tree(self, marks=None, arrows=None, base="done", label=None):
        cls = [base] * len(self.a)
        for i, c in (marks or {}).items():
            if 0 <= i < len(cls):
                cls[i] = c
        t = {"label": label or self.label, "v": [self.show(x) for x in self.a], "cls": cls}
        if arrows:
            t["arrows"] = [list(x) for x in arrows if 0 <= x[0] < len(cls) and 0 <= x[1] < len(cls)]
        return t

    def array(self, marks=None, base="done", label=None):
        cls = [base] * len(self.a)
        for i, c in (marks or {}).items():
            if 0 <= i < len(cls):
                cls[i] = c
        return {"label": label or "array", "v": [self.show(x) for x in self.a], "cls": cls}

    def _ev(self, text, marks=None, arrows=None):
        return {"tree": self.tree(marks, arrows), "array": self.array(marks), "text": text}

    # -- operations (each returns the list of recorded steps)
    def push(self, x, detail=True):
        self.a.append(x)
        i = len(self.a) - 1
        evs = [self._ev(f"Push {self.show(x)}: place it in the next free slot ({i}), then sift it <strong>up</strong>.",
                        {i: "cur"})]
        while i > 0:
            p = (i - 1) // 2
            if self._better(self.a[i], self.a[p]):
                if detail:
                    evs.append(self._ev(f"{self.show(self.a[i])} beats its parent {self.show(self.a[p])}: swap.",
                                        {i: "cur", p: "src"}, [(i, p), (p, i)]))
                self.a[i], self.a[p] = self.a[p], self.a[i]
                i = p
            else:
                if detail:
                    evs.append(self._ev(f"Parent {self.show(self.a[p])} is already {'smaller' if self.kind == 'min' else 'larger'}: stop.",
                                        {i: "cur", p: "src"}))
                break
        evs.append(self._ev(f"Heap order restored; {self.show(x)} settled at slot {i}.", {i: "chosen"}))
        return evs

    def pop(self, detail=True):
        """Remove the top. The popped value is in self.last_popped."""
        top = self.a[0]
        self.last_popped = top
        evs = [self._ev(f"Pop the top, {self.show(top)}. Move the last element into the root and sift it <strong>down</strong>.",
                        {0: "answer", len(self.a) - 1: "src"}, [(len(self.a) - 1, 0)] if len(self.a) > 1 else None)]
        last = self.a.pop()
        if self.a:
            self.a[0] = last
            evs += self._sift_down(0, detail)
        return evs

    def _sift_down(self, i, detail=True):
        evs, n = [], len(self.a)
        while True:
            l, r, best = 2 * i + 1, 2 * i + 2, i
            if l < n and self._better(self.a[l], self.a[best]):
                best = l
            if r < n and self._better(self.a[r], self.a[best]):
                best = r
            if best == i:
                if detail:
                    kids = [k for k in (l, r) if k < n]
                    evs.append(self._ev(
                        f"{self.show(self.a[i])} is {'no larger' if self.kind == 'min' else 'no smaller'} than its children: stop."
                        if kids else f"{self.show(self.a[i])} is a leaf: stop.",
                        {i: "chosen", **{k: "src" for k in kids}}))
                break
            if detail:
                evs.append(self._ev(f"{self.show(self.a[best])} is the {'smaller' if self.kind == 'min' else 'larger'} child "
                                    f"and beats {self.show(self.a[i])}: swap them.",
                                    {i: "cur", best: "src"}, [(i, best), (best, i)]))
            self.a[i], self.a[best] = self.a[best], self.a[i]
            i = best
        return evs

    def replace_top(self, x, detail=True):
        """heapreplace: pop the top and push x in one sift."""
        old = self.a[0]
        self.last_popped = old
        self.a[0] = x
        evs = [self._ev(f"Replace the top {self.show(old)} with {self.show(x)}, then sift down.", {0: "cur"})]
        return evs + self._sift_down(0, detail)

    def heapify(self, items, detail=True):
        self.a = list(items)
        n = len(self.a)
        evs = [self._ev("Start with the items in any order. Leaves (the second half) are already one-element heaps.",
                        {k: "dim" for k in range(n // 2, n)})]
        for i in range(n // 2 - 1, -1, -1):
            evs.append(self._ev(f"Sift down slot {i} ({self.show(self.a[i])}).", {i: "cur"}))
            evs += self._sift_down(i, detail)
        evs.append(self._ev("Every parent now beats its children: the array is a valid heap.", {0: "answer"}))
        return evs
