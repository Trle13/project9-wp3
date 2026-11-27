from collections import Counter

from streams import synthetic


def test_true_counts_small():
    for kind, kw in [("uniform", {"n_values": 10}), ("all_distinct", {}), ("zipf", {"s": 1.1, "n_values": 50}),
                     ("heavy_repeats", {"n_values": 7})]:
        items, true_count = synthetic.make(kind, 200, seed=3, **kw)
        assert len(items) == 200
        assert true_count == len(set(items))


def test_all_distinct_is_permutation():
    items, n = synthetic.all_distinct(50, seed=1)
    assert sorted(items) == list(range(1, 51)) and n == 50


def test_same_seed_same_stream():
    assert synthetic.zipf(100, 30, 1.5, seed=9) == synthetic.zipf(100, 30, 1.5, seed=9)


def test_reorder_keeps_multiset():
    base, n = synthetic.zipf(500, 100, 1.1, seed=2)
    for order in ("random", "sorted", "bursts", "new_last"):
        out, n2 = synthetic.reorder(base, order, seed=4)
        assert Counter(out) == Counter(base) and n2 == n


def test_orders_have_their_shape():
    base = [1, 2, 2, 3, 3, 3]
    assert synthetic.reorder(base, "sorted")[0] == [1, 2, 2, 3, 3, 3]
    out = synthetic.reorder(base, "new_last")[0]
    assert out == [3, 3, 3, 2, 2, 1]
    bursts = synthetic.reorder(base, "bursts", seed=5)[0]
    runs = [v for i, v in enumerate(bursts) if i == 0 or bursts[i - 1] != v]
    assert sorted(runs) == [1, 2, 3]          # every value appears as one contiguous block
