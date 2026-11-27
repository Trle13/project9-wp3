"""Exact baseline: a hash set (WP4 owns the final version; this one lets WP3 test the harness)."""
from .base import Estimator, ITEM_BYTES


class ExactSet(Estimator):
    name = "exact"

    def __init__(self, seed: int = 0, **params):
        self.items = set()

    def add(self, item) -> None:
        self.items.add(item)

    def estimate(self) -> float:
        return float(len(self.items))

    def memory_bytes(self) -> int:
        return len(self.items) * ITEM_BYTES

    def stats(self) -> dict:
        return {"stored": len(self.items), "halvings": 0, "failed": 0}
