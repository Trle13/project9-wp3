# WP3 reasoning — why the experiments are designed this way, and why the results look as they do

Two parts: **(A) design rationale** — for every choice, the question it answers and why it is the right choice;
**(B) interpretation** — why the measured numbers come out as they do, checked against a simple model.
All numbers below come from `results/summary_e1.md`, `summary_e2.md`, `summary_e5.md` and `summary_model.md`.

---

## A. Design rationale

**A1. The stream is fixed; only the algorithm's seed changes.**
The theorem says: *for every stream*, Pr{estimate outside (1 ± ε)F₀} ≤ δ, where the probability is over the
algorithm's own coin flips. To test exactly this statement, we fix one stream (stream seed 0) and repeat the
algorithm with 2,000 different coin seeds. If we also changed the stream between runs, we would be measuring an
average over random inputs, which is a different (weaker) claim.

**A2. Three stream shapes.**
- S1 uniform (63,249 distinct) is the neutral case.
- S2 all-distinct (100,000 distinct) gives the largest F₀ for a given length, so it forces the most halvings.
- S3 Zipf with s = 1.1 (23,999 distinct) has many repeats and a long tail, like real web traffic. It checks that
  repeated items are handled correctly (each distinct item must count once, however often it appears).
Together they cover "few repeats", "no repeats" and "heavy, skewed repeats". S4 (300 values) is used only in a
unit test: there F₀ is below the threshold, so CVM must return the exact count.

**A3. m = 100,000 and ε ∈ {0.2, 0.3, 0.5}.**
CVM only does something interesting when F₀ is much larger than the threshold; otherwise p stays 1 and the
answer is trivially exact. With ε = 0.05 the threshold would be 110,000–126,000 for this m, larger than every F₀ here, so we
chose ε values that give thresholds of 1,101–7,877, small enough for 2–7 halvings. The two values of δ
(0.01 and 0.1) change the threshold only a little (the log term), which itself is worth showing.

**A4. 2,000 seeds per setting.**
With k failures in n runs we can only claim an upper bound on the true failure probability. For k = 0 and
n = 2,000, the 95% Wilson upper bound is 0.0019, which lies below both δ = 0.01 and δ = 0.1. So 2,000 runs are
enough to confirm the guarantee for every δ we test, and the whole study still runs in 12 minutes.

**A5. A ⊥ output counts as a failure.**
The guarantee covers two bad events: the estimate is outside ±ε, or the algorithm gives up (⊥). Dropping ⊥ runs
would make the failure rate look better than it is, so they are recorded and counted.

**A6. Signed error in the histograms, absolute error in the tables.**
The signed error (estimate − F₀)/F₀ shows whether the estimator is biased (centre of the histogram) as well as
its spread; the absolute error is what the guarantee is about.

**A7. Threshold scale c = 1, 1/2, …, 1/256 (E2).**
The brief asks how conservative the theoretical threshold is. Halving c each step covers two orders of magnitude
on a log scale with only 9 points, which is enough to locate where the failure rate crosses δ.

**A8. E5 also uses 1/16 of the threshold.**
With the full threshold the errors are about 1%, so a small effect of the order would be invisible. At 1/16 the
errors are about 4%, large enough that a real difference between orders would show up.

**A9. One memory model for all estimators.**
"Stored items × 8 bytes" for CVM and the exact set, register bytes for HyperLogLog (WP4). For CVM we count the
full threshold, because that space must be reserved. Without a common unit, E3's comparison would be unfair.

---

## B. Interpretation of the results

### B1. One simple model explains almost every number

At the end of the stream, each of the F₀ distinct items is in the sample with probability p = 2^(−halvings)
(this is the key property the proof establishes). If we treat the items as independent, the sample size is
binomial, |X| ~ Bin(F₀, p), and the estimate |X|/p has relative standard deviation

  sd = √((1 − p) / (p · F₀))  ≈  1 / √(expected sample size).

So **the error depends only on how many items end up in the sample**, and the threshold controls that number.

How well this predicts the measurements (`results/summary_model.md`):

| setting | measured sd | model sd | measured failure rate | model failure rate |
|---|---|---|---|---|
| S2, ε = 0.2, δ = 0.1, full threshold (6,880) | 1.24% | 1.22% | 0 | ≈ 0 |
| S1, ε = 0.5, δ = 0.01, full threshold (1,261) | 3.13% | 3.16% | 0 | ≈ 0 |
| S1, E2, c = 1/32 (215) | 9.24% | 8.95% | 0.028 | 0.026 |
| S1, E2, c = 1/64 (108) | 12.70% | 12.53% | 0.105 | 0.111 |
| S3, E2, c = 1/64 (108) | 10.79% | 10.73% | 0.065 | 0.064 |

Across all 45 settings of E1 and E2, the model's standard deviation is within 7% of the measured one, and usually within 2%.

### B2. Why E1 never fails

With the full threshold the final sample holds thousands of items, so sd ≈ 1.1–3.6%. The allowed error ε is
20–50%, that is, 12 to 16 standard deviations away. A normal variable essentially never lands 14 sd from its
mean, so 0 failures in 36,000 runs is exactly what we should expect. The worst error we saw (5.3% for ε = 0.2,
13.7% for ε = 0.5) is 3–4 sd, a normal value for the most extreme of 2,000 runs.

### B3. Why the estimator is unbiased

Each distinct item is in the sample with probability p, so by linearity of expectation E[|X|] = p · F₀ and
E[|X|/p] = F₀ (Lecture 3: indicators + linearity). The data agree: in all 18 E1 settings the mean signed error
is between −0.07% and +0.13%, never more than 2 standard errors from 0, so no bias is detectable.

### B4. Why the threshold is about 32× (or more) larger than needed

For the failure rate to stay below δ = 0.1, the error must stay within ε = 0.2 in 90% of runs, i.e.
ε ≥ 1.645 sd. That needs a final sample of about (1.645 / 0.2)² ≈ 68 items. The final sample lies between half
the threshold and the full threshold, so a threshold of roughly 70–135 would be enough, that is c ≈ 1/100 to
1/50. E2 agrees: the failure rate reaches δ around c = 1/64 (S1 just above δ there, S2 and S3 just below).

The paper's threshold (6,880 here) is far larger because the proof must hold in the worst case, with simple tools:
- the **Chernoff bound** uses a safe constant (the 12 in 12/ε²) instead of the exact normal tail;
- the **union bound** adds up the failure chances at every position of the stream and every value of p, which is
  where the log₂(8m/δ) ≈ 23 factor comes from, even though failures at different positions are strongly related;
- it must hold for **every** stream and every F₀, not just the ones we tried.
None of this is a flaw: a proof needs a bound that is always true, and simple bounds give away constant factors.
The experiment measures how large those factors are in practice.

### B5. Why no run ever returned ⊥

⊥ happens only if, after a halving, the sample is still full, i.e. **every** one of the threshold items survives
its coin flip. That has probability (1/2)^threshold: about 7·10⁻⁹ even for the smallest threshold we tried (27),
and astronomically small for the real thresholds. So the ⊥ case matters for the proof but never in practice.

### B6. Why the order does not matter (E5)

After an item's last occurrence, whether it is in the sample depends only on the coin flips made at and after
that moment, and every distinct item faces the same chances. So the distribution of |X| depends on F₀ and the
coins, not on the order of the stream. E5 confirms it: mean errors of 0.88–0.92% (full threshold) and
3.94–4.11% (1/16 threshold) for all four orders, differences well inside the random variation.
(The theorem allows any order fixed in advance; an adversary who sees the coins and adapts the stream is a
different setting that we do not test.)

### B7. Why the number of halvings is predictable

CVM halves whenever the sample fills, so after k halvings it holds about F₀/2^k items. It stops halving once
F₀/2^k drops below the threshold. For S2 with threshold 6,880: 100,000/16 = 6,250 < 6,880, so 4 halvings, as
measured. For S3: 23,999/4 ≈ 6,000, so 2 halvings, as measured. This also confirms the implementation behaves as
the algorithm says.

---

## Limits of this reasoning (say this in the report)

- The binomial model treats items as independent and uses a normal approximation; it explains the numbers but
  does not replace the proof (WP1).
- 2,000 runs cannot see failure probabilities below about 0.2%.
- m = 100,000 only; the final paper repeats E1 and E2 at m = 10⁶ and adds real streams (E4) and the baselines (E3).
