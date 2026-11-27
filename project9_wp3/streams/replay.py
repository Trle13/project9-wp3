"""Live-demo replay: feed a stream at a fixed rate and print the running estimates.

    python -m streams.replay --rate 200000 --seconds 20

Shows CVM next to the exact count, plus the measured items per second.
"""
import argparse
import time

from estimators.cvm_reference import CVM
from estimators.exact import ExactSet
from streams import synthetic


def replay(items, rate: float):
    """Yield items at about `rate` items per second (in batches, so the clock is checked rarely)."""
    batch = max(1, int(rate // 100))
    t0 = time.perf_counter()
    for i in range(0, len(items), batch):
        target = t0 + i / rate
        delay = target - time.perf_counter()
        if delay > 0:
            time.sleep(delay)
        yield from items[i:i + batch]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", type=float, default=200_000)
    ap.add_argument("--seconds", type=float, default=15)
    ap.add_argument("--eps", type=float, default=0.1)
    ap.add_argument("--delta", type=float, default=0.01)
    args = ap.parse_args()
    m = int(args.rate * args.seconds)
    items, true_count = synthetic.zipf(m, 10 * m, 1.1, seed=7)
    cvm, exact = CVM(seed=1, eps=args.eps, delta=args.delta, m=m), ExactSet()
    t0 = last = time.perf_counter()
    for n, x in enumerate(replay(items, args.rate), 1):
        cvm.add(x)
        exact.add(x)
        now = time.perf_counter()
        if now - last >= 1 or n == m:
            e, t = cvm.estimate(), exact.estimate()
            print(f"{now - t0:5.1f}s  items {n:>9,}  ({n / (now - t0):>9,.0f}/s)  "
                  f"exact {t:>9,.0f}  CVM {e:>11,.0f}  error {abs(e - t) / t:6.2%}  "
                  f"stored {len(cvm.X):>6,} of {cvm.thresh:,}")
            last = now


if __name__ == "__main__":
    main()
