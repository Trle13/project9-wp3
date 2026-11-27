"""WP3 harness: estimator x stream x seeds -> one CSV row per run.

    python -m experiments.e1_accuracy        (each experiment script calls run_configs)

Design:
- the stream is fixed by `stream_seed`; only the estimator's seed changes between runs,
  so the spread of the results comes from the algorithm's own coins;
- a failed run (CVM's FAIL) is written with failed=1 and an empty estimate, never dropped;
- resumable: (config_id, seed) pairs already in the CSV are skipped;
- seeds are split over CPU cores with multiprocessing.
"""
import csv
import json
import math
import os
import time
from multiprocessing import Pool

from experiments.registry import ESTIMATORS
from streams import synthetic

COLUMNS = ["experiment", "config_id", "estimator", "eps", "delta", "thresh_scale", "stream",
           "stream_params", "m", "stream_seed", "seed", "true_count", "estimate", "rel_error",
           "failed", "stored", "halvings", "thresh", "memory_bytes", "ns_per_item"]


def config_id(cfg: dict) -> str:
    keys = ("estimator", "est_params", "stream", "stream_params", "m", "stream_seed")
    return json.dumps({k: cfg[k] for k in keys}, sort_keys=True)


_cache = {}


def _stream(cfg):
    key = (cfg["stream"], json.dumps(cfg["stream_params"], sort_keys=True), cfg["m"], cfg["stream_seed"])
    if key not in _cache:
        _cache.clear()                    # keep only one stream in memory per worker
        _cache[key] = synthetic.make(cfg["stream"], cfg["m"], cfg["stream_seed"], **cfg["stream_params"])
    return _cache[key]


def run_one(cfg: dict, seed: int) -> dict:
    items, true_count = _stream(cfg)
    params = dict(cfg["est_params"])
    est = ESTIMATORS[cfg["estimator"]](seed=seed, m=cfg["m"], **params)
    add = est.add
    t0 = time.perf_counter_ns()
    for x in items:
        add(x)
    ns = (time.perf_counter_ns() - t0) / len(items)
    st = est.stats()
    e = est.estimate()
    failed = int(st.get("failed", 0) or math.isnan(e))
    return {
        "experiment": cfg["experiment"], "config_id": config_id(cfg), "estimator": cfg["estimator"],
        "eps": params.get("eps", ""), "delta": params.get("delta", ""),
        "thresh_scale": params.get("thresh_scale", 1.0), "stream": cfg["stream"],
        "stream_params": json.dumps(cfg["stream_params"], sort_keys=True), "m": cfg["m"],
        "stream_seed": cfg["stream_seed"], "seed": seed, "true_count": true_count,
        "estimate": "" if failed else e, "rel_error": "" if failed else abs(e - true_count) / true_count,
        "failed": failed, "stored": st.get("stored", ""), "halvings": st.get("halvings", ""),
        "thresh": st.get("thresh", ""), "memory_bytes": est.memory_bytes(), "ns_per_item": round(ns, 1),
    }


def _work(args):
    cfg, seeds = args
    return [run_one(cfg, s) for s in seeds]


def _done(path):
    if not os.path.exists(path):
        return set()
    with open(path, newline="") as f:
        return {(r["config_id"], int(r["seed"])) for r in csv.DictReader(f)}


def run_configs(configs, path, processes=None, chunk=25, verbose=True):
    """Run every config for seeds 0..n_seeds-1, appending rows to the CSV at `path`."""
    done = _done(path)
    tasks = []
    for cfg in configs:
        cid = config_id(cfg)
        todo = [s for s in range(cfg["n_seeds"]) if (cid, s) not in done]
        tasks += [(cfg, todo[i:i + chunk]) for i in range(0, len(todo), chunk)]
    if verbose:
        print(f"{len(configs)} configs, {sum(len(t[1]) for t in tasks)} runs to do -> {path}")
    if not tasks:
        return
    new = not os.path.exists(path)
    t0 = time.time()
    with open(path, "a", newline="") as f, Pool(processes or os.cpu_count()) as pool:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new:
            w.writeheader()
        for i, rows in enumerate(pool.imap_unordered(_work, tasks), 1):
            w.writerows(rows)
            f.flush()
            if verbose and (i % 20 == 0 or i == len(tasks)):
                print(f"  {i}/{len(tasks)} chunks, {time.time() - t0:,.0f}s")
