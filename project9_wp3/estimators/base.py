"""The shared estimator interface agreed between WP2, WP3 and WP4.

Every estimator (CVM, exact set, HyperLogLog, KMV) implements these five
methods, so the WP3 harness can run any of them without special cases.
"""
from abc import ABC, abstractmethod

ITEM_BYTES = 8  # memory model: one stored stream item = one 64-bit identifier


class Estimator(ABC):
    @abstractmethod
    def __init__(self, seed: int = 0, **params): ...

    @abstractmethod
    def add(self, item) -> None:
        """Process one stream item."""

    @abstractmethod
    def estimate(self) -> float:
        """Current estimate of the number of distinct items (NaN if the run failed)."""

    @abstractmethod
    def memory_bytes(self) -> int:
        """Memory used, in bytes, under the common memory model."""

    def stats(self) -> dict:
        """Extra counters, e.g. {'stored': ..., 'halvings': ..., 'failed': ...}."""
        return {}
