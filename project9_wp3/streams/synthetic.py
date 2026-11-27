"""Synthetic streams with a known number of distinct items (WP3, streams S1-S5).

Every generator returns (items, true_count): items is a plain Python list of
ints (fast to iterate), true_count is computed exactly with a set.
"""
from collections import Counter

import numpy as np


def _result(arr):
    items = [int(x) for x in arr]
    return items, len(set(items))


def uniform(m: int, n_values: int, seed: int = 0):
    """S1: m draws, each value in {1..n_values} equally likely."""
    rng = np.random.default_rng(seed)
    return _result(rng.integers(1, n_values + 1, size=m))


def all_distinct(m: int, seed: int = 0):
    """S2: 1, 2, ..., m in a random order (distinct count = m)."""
    rng = np.random.default_rng(seed)
    return _result(rng.permutation(np.arange(1, m + 1)))


def zipf(m: int, n_values: int, s: float, seed: int = 0):
    """S3: m draws from {1..n_values}, value k with probability proportional to 1/k^s.

    numpy's own zipf sampler only works for s > 1 and has no upper limit, so the
    probabilities over the n_values values are built directly.
    """
    rng = np.random.default_rng(seed)
    k = np.arange(1, n_values + 1, dtype=float)
    p = k ** -s
    p /= p.sum()
    return _result(rng.choice(n_values, size=m, p=p) + 1)


def heavy_repeats(m: int, n_values: int = 300, seed: int = 0):
    """S4: a few hundred values repeated to length m (fewer distinct items than the threshold)."""
    rng = np.random.default_rng(seed)
    return _result(rng.integers(1, n_values + 1, size=m))


def reorder(items, order: str, seed: int = 0):
    """S5: the same items in another order (the multiset, hence the distinct count, is unchanged).

    random   - shuffled
    sorted   - ascending by value
    bursts   - all copies of a value next to each other, values in random order
    new_last - most frequent values first, values that occur once at the very end
    """
    rng = np.random.default_rng(seed)
    if order == "random":
        out = list(items)
        rng.shuffle(out)
    elif order == "sorted":
        out = sorted(items)
    elif order in ("bursts", "new_last"):
        counts = Counter(items)
        values = list(counts)
        rng.shuffle(values)
        if order == "new_last":
            values.sort(key=lambda v: -counts[v])      # stable: ties keep the random order
        out = [v for v in values for _ in range(counts[v])]
    else:
        raise ValueError(f"unknown order {order!r}")
    return out, len(set(out))


def make(kind: str, m: int, seed: int = 0, **kw):
    """Build a stream by name, e.g. make('zipf', 10**5, s=1.1, n_values=10**6)."""
    if kind == "uniform":
        return uniform(m, kw.get("n_values", m), seed)
    if kind == "all_distinct":
        return all_distinct(m, seed)
    if kind == "zipf":
        return zipf(m, kw.get("n_values", m), kw["s"], seed)
    if kind == "heavy_repeats":
        return heavy_repeats(m, kw.get("n_values", 300), seed)
    if kind == "reordered":
        base, _ = make(kw["base"], m, seed, **{k: v for k, v in kw.items() if k not in ("base", "order")})
        return reorder(base, kw["order"], seed + 1)
    raise ValueError(f"unknown stream kind {kind!r}")
