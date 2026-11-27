import csv
import math

from estimators.cvm_reference import CVM, cvm_threshold
from experiments.run import run_configs, run_one


def cfg(estimator, est_params, stream="uniform", sp=None, m=2000, n_seeds=5):
    return {"experiment": "test", "estimator": estimator, "est_params": est_params, "stream": stream,
            "stream_params": sp if sp is not None else {"n_values": 1000}, "m": m, "stream_seed": 0,
            "n_seeds": n_seeds}


def test_exact_has_zero_error(tmp_path):
    path = tmp_path / "r.csv"
    run_configs([cfg("exact", {})], str(path), processes=1, verbose=False)
    rows = list(csv.DictReader(open(path)))
    assert len(rows) == 5 and all(float(r["rel_error"]) == 0 for r in rows)


def test_resumable(tmp_path):
    path = str(tmp_path / "r.csv")
    run_configs([cfg("exact", {}, n_seeds=3)], path, processes=1, verbose=False)
    run_configs([cfg("exact", {}, n_seeds=5)], path, processes=1, verbose=False)
    seeds = sorted(int(r["seed"]) for r in csv.DictReader(open(path)))
    assert seeds == [0, 1, 2, 3, 4]                 # nothing ran twice


def test_cvm_exact_below_threshold():
    # fewer distinct items than the threshold: p stays 1, so CVM returns the exact count
    r = run_one(cfg("cvm", {"eps": 0.5, "delta": 0.1}, stream="heavy_repeats", sp={"n_values": 300}), 0)
    assert r["halvings"] == 0 and float(r["estimate"]) == r["true_count"]


def test_cvm_repeated_item_counts_once():
    c = CVM(seed=1, eps=0.5, delta=0.1, m=1000)
    for _ in range(1000):
        c.add("same")
    assert c.estimate() == 1


def test_cvm_invariants():
    c = CVM(seed=3, eps=0.5, delta=0.1, m=50_000, thresh_scale=0.05)
    for x in range(50_000):
        c.add(x)
        assert len(c.X) < c.thresh
    assert c.p == 0.5 ** c.halvings and not math.isnan(c.estimate())


def test_threshold_formula():
    assert cvm_threshold(0.1, 0.01, 10 ** 6) == 35491
