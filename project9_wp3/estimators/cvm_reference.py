"""Reference CVM implementation used ONLY to test the WP3 pipeline.

WP2 owns the official implementation; when it is ready, register it in
experiments/registry.py and the harness runs it unchanged.

Algorithm (Chakraborty, Vinodchandran, Meel, ESA 2022, Algorithm 1):
    p = 1, X = {}, thresh = ceil(12/eps^2 * log2(8m/delta))
    for each item a:
        remove a from X
        with probability p: add a to X
        if |X| == thresh:
            keep each element of X with probability 1/2;  p = p/2
            if |X| == thresh: output FAIL
    output |X| / p
"""
import math
import random

from .base import Estimator, ITEM_BYTES


def cvm_threshold(eps: float, delta: float, m: int) -> int:
    return math.ceil(12 / eps ** 2 * math.log2(8 * m / delta))


class CVM(Estimator):
    name = "cvm"

    def __init__(self, seed: int = 0, eps: float = 0.1, delta: float = 0.01, m: int = 10 ** 6,
                 thresh_scale: float = 1.0, **params):
        self.rng = random.Random(seed)
        self.thresh = max(2, math.ceil(thresh_scale * cvm_threshold(eps, delta, m)))
        self.p = 1.0
        # dict instead of set: iteration order = insertion order, so a run is
        # reproducible from its seed even for string items (Python randomises str hashes)
        self.X = {}
        self.halvings = 0
        self.max_stored = 0
        self.failed = False

    def add(self, item) -> None:
        if self.failed:
            return
        X = self.X
        X.pop(item, None)                      # 1. remove the item if present
        if self.p == 1.0 or self.rng.random() < self.p:
            X[item] = None                     # 2. keep it with probability p
            if len(X) > self.max_stored:
                self.max_stored = len(X)
            if len(X) == self.thresh:          # 3. sample full: halve
                rnd = self.rng.random
                self.X = X = {x: None for x in X if rnd() < 0.5}
                self.p /= 2
                self.halvings += 1
                if len(X) == self.thresh:      # still full: the algorithm reports FAIL
                    self.failed = True

    def estimate(self) -> float:
        return float("nan") if self.failed else len(self.X) / self.p

    def memory_bytes(self) -> int:
        return self.thresh * ITEM_BYTES        # space reserved for the full sample

    def stats(self) -> dict:
        return {"stored": self.max_stored, "halvings": self.halvings, "failed": int(self.failed),
                "thresh": self.thresh}
