"""Compare the measured spread of CVM's error with a simple binomial model.

Model: at the end of the stream each of the F0 distinct items is in the sample with probability p = 2^-halvings,
so |X| ~ Binomial(F0, p) and the estimate |X|/p has relative standard deviation sqrt((1 - p) / (p * F0)).
A normal approximation then predicts Pr{|error| > eps} = erfc(eps / (sd * sqrt(2))).
This is an explanation of the numbers, not a proof (the proof needs the Chernoff and union bounds).

    python -m experiments.model_check      -> results/summary_model.md
"""
import math

import numpy as np
import pandas as pd

NAMES = {"uniform": "S1 uniform", "all_distinct": "S2 all-distinct", "zipf": "S3 Zipf s=1.1"}


def table(name):
    df = pd.read_csv(f"results/{name}.csv")
    df["est"] = pd.to_numeric(df["estimate"], errors="coerce")
    df["p"] = 0.5 ** df["halvings"]
    df["signed"] = (df["est"] - df["true_count"]) / df["true_count"]
    df["sd_model"] = np.sqrt((1 - df["p"]) / (df["p"] * df["true_count"]))
    df["fail_model"] = [math.erfc(e / (s * math.sqrt(2))) if s > 0 else 0.0 for e, s in zip(df["eps"], df["sd_model"])]
    df["fail_obs"] = (df["failed"] == 1) | (df["signed"].abs() > df["eps"])
    out = df.groupby(["stream", "eps", "delta", "thresh_scale"]).agg(
        threshold=("thresh", "first"), sd_obs=("signed", "std"), sd_model=("sd_model", "mean"),
        fail_obs=("fail_obs", "mean"), fail_model=("fail_model", "mean")).reset_index()
    out["stream"] = out["stream"].map(NAMES)
    return out


def md(out, title):
    lines = [f"## {title}", "", "| stream | ε | δ | scale c | threshold | measured sd % | model sd % | measured fail rate | model fail rate |",
             "|---|---|---|---|---|---|---|---|---|"]
    for _, r in out.iterrows():
        c = "1" if r.thresh_scale == 1 else f"1/{round(1 / r.thresh_scale)}"
        lines.append(f"| {r.stream} | {r.eps:g} | {r.delta:g} | {c} | {int(r.threshold):,} | {100 * r.sd_obs:.2f} | "
                     f"{100 * r.sd_model:.2f} | {r.fail_obs:.4f} | {r.fail_model:.4f} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    with open("results/summary_model.md", "w") as f:
        f.write("# Binomial model vs measurements\n\n" + md(table("e1"), "E1") + "\n" + md(table("e2"), "E2"))
    print("written results/summary_model.md")
