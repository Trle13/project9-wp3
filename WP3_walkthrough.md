# WP3 walkthrough — what each part does and why

Read this before the meetings and the defense: every design choice below is something an examiner can ask about.

## 1. The big picture

```
streams/  ──►  experiments/run.py  ──►  results/*.csv  ──►  experiments/analyze.py  ──►  figures/ + summary tables
 (input)        (the harness)            (raw data)           (statistics + plots)
```

The harness never knows which estimator it runs: it only calls the five methods of the shared interface
(`estimators/base.py`). That is why WP2's CVM and WP4's baselines plug in without changes.

## 2. Streams (`streams/synthetic.py`)

| Stream | What it is | Why it is in the study |
|---|---|---|
| S1 uniform | 100,000 draws from {1..100,000} → about 63,000 distinct | the simple, fair case |
| S2 all-distinct | 1..100,000 shuffled → 100,000 distinct | the most halvings for a given length |
| S3 Zipf s = 1.1 | 100,000 draws, value k with probability ∝ 1/k^1.1 → about 24,000 distinct | looks like real web traffic: a few very common items, a long tail |
| S4 heavy repeats | 300 values repeated | fewer distinct items than the threshold: CVM must be exact (unit test) |
| S5 reorders | the S3 items sorted, in bursts, or with the new items last | tests "any order fixed in advance" |

- Every generator returns `(items, true_count)`. The true count comes from a Python `set`, so the truth is exact.
- Zipf: numpy's built-in `zipf` only works for s > 1 and has no upper limit, so we build the probabilities
  1/k^s over 1,000,000 values ourselves and draw with `rng.choice`.
- `streams/real.py` reads any log file line by line and takes one field (e.g. the client host). It is ready for
  E4 once the team picks two public logs.
- `streams/replay.py` is the live demo: it feeds a stream at a fixed rate and prints CVM next to the exact count.

## 3. The harness (`experiments/run.py`)

Key ideas, each one a likely exam question:

1. **Two seeds, kept apart.** The stream seed fixes the input; only the estimator's seed changes between runs.
   So the spread we measure comes from CVM's own coins — exactly what the (ε, δ) theorem is about
   ("Pr is over the random choices of the algorithm").
2. **Failures are never dropped.** If CVM outputs FAIL (⊥), the row is written with `failed = 1`.
   A run "fails the guarantee" if it returned FAIL **or** its relative error is above ε.
3. **Resumable.** Before running, the harness reads the CSV and skips (configuration, seed) pairs already done,
   so a crash loses nothing.
4. **Parallel.** Runs for different seeds are independent, so they are spread over CPU cores.
5. **One CSV row per run** with every number we may need later (error, halvings, stored items, memory, time),
   so a new plot never needs a new run.

Relative error = |estimate − true count| / true count.

## 4. Why the observed failure rate needs an upper bound

With 2,000 runs and 0 failures, the true failure probability is not proven to be 0. The 95% Wilson interval
gives an **upper bound**: for 0 failures in 2,000 runs it is about 0.0019. So we can say "the failure
probability is below 0.2% with 95% confidence", which is below both δ = 0.01 and δ = 0.1.

## 5. The experiments

- **E1** — Does CVM keep its promise? 3 streams × ε ∈ {0.2, 0.3, 0.5} × δ ∈ {0.01, 0.1}, 2,000 seeds each.
- **E2** — How conservative is the threshold? Same setup with the threshold multiplied by c = 1, 1/2, …, 1/256.
  This is the question the brief singles out.
- **E5** — Does the order matter? The same S3 items in 4 orders, with the full threshold and with 1/16 of it
  (so the errors are big enough to compare).
- **E3, E4** — wait for WP4's HyperLogLog/KMV and the real logs; the harness already supports them.

## 6. Why m = 100,000 and not 10⁶

The paper's threshold is large (6,880 stored items for ε = 0.2, δ = 0.1, m = 10⁵). The stream must have many more
distinct items than the threshold, or CVM never halves and is trivially exact. With m = 10⁵ we get several
halvings and a run takes about 15 ms in pure Python, so 2,000 seeds per setting finish in minutes.
For the final paper, the same scripts run with m = 10⁶ (about 10× longer).

## 7. The memory model

Every estimator reports memory as "stored items × 8 bytes" (a 64-bit identifier per item). For CVM we count
the full threshold, the space it must reserve. WP4 reports HyperLogLog's registers in bytes, so E3 compares
everything in the same unit.

## 8. How WP2 and WP4 plug in

1. Their class implements `Estimator` (`add`, `estimate`, `memory_bytes`, `stats`).
2. Add one line to `experiments/registry.py`, e.g. `"hll": HyperLogLog`.
3. Re-run an experiment script — nothing else changes.

`estimators/cvm_reference.py` is only our test stand-in for WP2's code; the report must use WP2's official version
(or state clearly which one was used).
