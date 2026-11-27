# Project 9 — WP3 experiment pipeline

Streams, harness, experiments and figures for "Distinct Elements in Streams: An Algorithm for the (Text) Book"
(Chakraborty, Vinodchandran, Meel, ESA 2022). WP3 owner: Lê Vũ Thanh Trúc.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install numpy pandas matplotlib pytest
```
Python 3.10+. Run every command from this folder.

## Commands

| Command | What it does | Time (2 cores) |
|---|---|---|
| `python -m pytest -q tests` | Unit tests for streams, harness and the reference CVM | < 1 s |
| `python -m experiments.run_all` | Runs E1, E2, E5 into `results/*.csv` (resumable) | about 15 min |
| `python -m experiments.run_all E1` | Only one experiment | |
| `python -m experiments.analyze` | Figures into `figures/`, tables into `results/summary_*.md` | < 1 min |
| `python -m experiments.model_check` | Binomial model vs measured spread → `results/summary_model.md` | < 1 min |
| `python -m streams.replay --rate 200000 --seconds 15` | Live demo: CVM vs exact count on a fast stream | 15 s |

## Layout

```
estimators/   base.py (shared interface), exact.py, cvm_reference.py (test stand-in for WP2's CVM)
streams/      synthetic.py (S1–S5), real.py (log-file loader for E4), replay.py (live demo)
experiments/  run.py (harness), configs.py (E1, E2, E5), run_all.py, analyze.py, registry.py
tests/        test_streams.py, test_harness.py
results/      raw CSV, one row per run (never edit by hand) + summary tables
figures/      e1_error_hist.png, e2_threshold.png, e5_order.png
report/       WP3_walkthrough.md (how it works), experimental_setup.md (text for the report),
              reasoning.md (design rationale + why the results look as they do)
```

## Plugging in WP2 and WP4

Implement `estimators/base.Estimator`, add the class to `experiments/registry.py`
(e.g. `"hll": HyperLogLog`), and re-run. E3 (baselines at equal memory) and E4 (real logs) need
WP4's classes and two chosen log files; the harness and the log loader are ready.

## Results so far

See `report/experimental_setup.md` and `results/summary_e1.md`, `summary_e2.md`, `summary_e5.md`.

Key findings (details in `report/experimental_setup.md`):
- **E1:** 36,000 runs over 18 settings, 0 failures and 0 FAIL outputs; the worst error was just over a quarter of ε.
- **E2:** with ε = 0.2, δ = 0.1, a threshold about 32× smaller than the paper's still keeps failures below δ.
- **E5:** sorted, burst and "new items last" orders give the same error as a random order.

## AI use (for the AI Disclosure Statement)

This WP3 code, the experiment runs and the draft texts in `report/` were produced with the help of an AI
assistant (Claude), at the WP3 owner's request; the owner reviewed them and must be able to explain every part
(see `report/WP3_walkthrough.md`). Declare this in the team's AI Disclosure Statement.
