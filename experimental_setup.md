# Experiments (WP3) — text for the midterm write-up

## Experimental setup

**Algorithm under test.** CVM exactly as in Algorithm 1 of the paper: threshold ⌈12/ε² · log₂(8m/δ)⌉,
remove-then-resample on every item, halving of the sample and of p when the sample is full, output ⊥ if the
sample is still full after a halving. (This run used the WP3 reference implementation; the final report will
use WP2's implementation through the same interface.)

**Streams.** All streams have length m = 100,000 and an exact distinct count computed with a hash set:
S1 uniform over 100,000 values (63,249 distinct), S2 all-distinct (100,000 distinct), and S3 Zipf with
exponent s = 1.1 over 1,000,000 values (23,999 distinct). Each stream is generated once from a fixed seed;
only the algorithm's random seed varies between runs, so the observed spread is due to the algorithm's coins,
which is the probability space of the (ε, δ) guarantee.

**Runs and metrics.** Each configuration is run with 2,000 independent seeds. For each run we record the
estimate, the relative error |estimate − F₀| / F₀, whether the run output ⊥, the largest sample size, the number
of halvings and the time per item. A run *fails the guarantee* if it outputs ⊥ or its relative error exceeds ε.
We report the observed failure rate with the upper end of its 95% Wilson interval (0.0019 when 0 of 2,000 runs
fail). Experiments ran in Python 3.13 on 2 CPU cores; E1, E2 and E5 together (106,000 runs) took 12 minutes.

## Results

**E1 — the guarantee holds with a wide margin (Figure e1_error_hist.png, Table summary_e1.md).**
Over 18 configurations (3 streams × ε ∈ {0.2, 0.3, 0.5} × δ ∈ {0.01, 0.1}) and 36,000 runs, no run failed the
guarantee and no run output ⊥. The largest relative error was 5.3% for ε = 0.2, 8.3% for ε = 0.3 and
13.7% for ε = 0.5, so even the worst run used only just over a quarter of the allowed error. The 95th-percentile
error was 2.2–3.1% for ε = 0.2. The number of halvings matched the expectation from the stream size, for example
4 halvings for S2 (100,000 distinct, threshold 6,880–7,877) and 2 for S3 (23,999 distinct).

**E2 — the threshold is conservative by a factor of about 32 (Figure e2_threshold.png, Table summary_e2.md).**
With ε = 0.2 and δ = 0.1, we multiplied the paper's threshold (6,880) by c = 1, 1/2, …, 1/256. Up to c = 1/8
(860 stored items) no run failed on any stream. At c = 1/32 (215 items) the failure rate was still 1.3–2.8%,
well below δ = 0.1. At c = 1/64 (108 items) it reached 6.5–10.5%, and the uniform stream crossed δ. So in this
setting a sample about 32 times smaller than the theorem's threshold already meets the (ε, δ) target. This is
expected: the proof uses a Chernoff bound and a union bound over all levels and stream positions, and both
steps give away constant factors. Even at c = 1/256 (27 items) no run output ⊥; failures came only from
estimates outside ±ε.

**E5 — the order of the stream does not matter (Figure e5_order.png, Table summary_e5.md).**
The same S3 items in random, sorted, burst and "new items last" order gave the same error distribution:
mean error 0.88–0.92% with the full threshold and 3.94–4.11% with 1/16 of it. This matches the guarantee,
which holds for any order fixed before the algorithm's coins are flipped.

**Not yet run.** E3 (CVM against HyperLogLog and KMV at equal memory) waits for WP4's baselines;
E4 (real logs) waits for the two datasets the team will choose. The harness and the log loader are ready for both.

## Threats to validity (to discuss)

- m = 100,000 keeps runs fast but limits how many halvings occur; the final paper repeats E1 and E2 at m = 10⁶.
- 2,000 runs can only show failure probabilities above roughly 0.2%; smaller values of δ (e.g. 0.01) can be
  confirmed only as "below 0.0019 with 95% confidence".
- The time per item (115–190 ns in pure Python) measures our implementation, not the algorithm; compare
  estimators only within the same language.
