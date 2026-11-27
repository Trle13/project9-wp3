"""Turn results/*.csv into figures/ and results/summary_*.md (one function per figure).

    python -m experiments.analyze
"""
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from experiments.configs import E2_SCALES, E5_ORDERS, STREAMS

SERIES = ["#257de0", "#f47230", "#00b894"]          # categorical slots 1-3, fixed order
REF, INK, MUTED, GRID = "#6b7280", "#1f2937", "#6b7280", "#e5e7eb"
NAMES = {kind: name for name, (kind, _) in STREAMS.items()}
ORDER_NAMES = {"random": "random", "sorted": "sorted", "bursts": "bursts", "new_last": "new items last"}

plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.titlesize": 11, "axes.titlecolor": INK, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "figure.dpi": 150})


def wilson_upper(k, n, z=1.96):
    """Upper end of the 95% Wilson interval for k failures in n runs."""
    if n == 0:
        return float("nan")
    p = k / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre + half) / (1 + z * z / n)


def load(name):
    df = pd.read_csv(f"results/{name}.csv")
    df["rel_error"] = pd.to_numeric(df["rel_error"], errors="coerce")
    df["estimate"] = pd.to_numeric(df["estimate"], errors="coerce")
    df["signed"] = (df["estimate"] - df["true_count"]) / df["true_count"]
    df["fails_guarantee"] = (df["failed"] == 1) | (df["rel_error"] > df["eps"])
    return df


def summarise(g):
    n, k = len(g), int(g["fails_guarantee"].sum())
    return pd.Series({
        "runs": n, "threshold": int(g["thresh"].iloc[0]), "true count": int(g["true_count"].iloc[0]),
        "mean |err| %": 100 * g["rel_error"].mean(), "95th pct |err| %": 100 * g["rel_error"].quantile(0.95),
        "max |err| %": 100 * g["rel_error"].max(), "fails (>eps or FAIL)": k, "FAIL outputs": int(g["failed"].sum()),
        "observed rate": k / n, "95% upper bound": wilson_upper(k, n),
        "mean halvings": g["halvings"].mean(), "ns/item": g["ns_per_item"].median()})


INT_COLS = {"runs", "threshold", "true count", "fails (>eps or FAIL)", "FAIL outputs"}


def md_table(df, floatfmt=None):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if c in INT_COLS:
                cells.append(f"{int(v):,}")
            elif c in ("ε", "δ", "scale c", "eps", "delta"):
                cells.append(f"{v:g}" if not (c == "scale c" and v < 1) else f"1/{round(1 / v)}")
            elif isinstance(v, float):
                cells.append(f"{v:.4f}" if c in ("observed rate", "95% upper bound") else f"{v:,.2f}")
            elif isinstance(v, (int, np.integer)):
                cells.append(f"{v:,}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def e1():
    df = load("e1")
    df["stream_name"] = df["stream"].map(NAMES)
    tab = df.groupby(["stream_name", "eps", "delta"]).apply(summarise, include_groups=False).reset_index()
    tab = tab.rename(columns={"stream_name": "stream", "eps": "ε", "delta": "δ"})
    with open("results/summary_e1.md", "w") as f:
        f.write("# E1 — CVM accuracy (m = 100,000, 2,000 seeds per row)\n\n" + md_table(tab) + "\n")
    eps_list, delta_list = sorted(df["eps"].unique()), sorted(df["delta"].unique())
    fig, axes = plt.subplots(len(delta_list), len(eps_list), figsize=(10, 5.6), sharey="row")
    for i, d in enumerate(delta_list):
        for j, e in enumerate(eps_list):
            ax = axes[i][j]
            sub = df[(df["eps"] == e) & (df["delta"] == d)]
            bins = np.linspace(-e * 1.15, e * 1.15, 93)
            for c, kind in zip(SERIES, NAMES):
                s = sub[sub["stream"] == kind]["signed"].dropna() * 100
                ax.hist(s, bins=bins * 100, histtype="step", linewidth=1.6, color=c, label=NAMES[kind])
            for x in (-e * 100, e * 100):
                ax.axvline(x, color=REF, linestyle="--", linewidth=1.2)
            ax.set_title(f"ε = {e:g}, δ = {d:g}")
            if i == len(delta_list) - 1:
                ax.set_xlabel("signed relative error (%)")
            if j == 0:
                ax.set_ylabel("runs (of 2,000)")
    axes[0][0].legend(loc="upper left", fontsize=8.5)
    fig.suptitle("E1: every CVM error falls far inside the ±ε band the theorem allows (dashed lines = ±ε)", x=0.01, ha="left",
                 color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig("figures/e1_error_hist.png")
    plt.close(fig)
    return tab


def e2():
    df = load("e2")
    df["stream_name"] = df["stream"].map(NAMES)
    tab = df.groupby(["stream_name", "thresh_scale"]).apply(summarise, include_groups=False).reset_index()
    tab = tab.sort_values(["stream_name", "thresh_scale"], ascending=[True, False])
    out = tab.rename(columns={"stream_name": "stream", "thresh_scale": "scale c"})
    with open("results/summary_e2.md", "w") as f:
        f.write("# E2 — threshold scaled by c (ε = 0.2, δ = 0.1, m = 100,000, 2,000 seeds per row)\n\n"
                + md_table(out) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9))
    for c, kind in zip(SERIES, NAMES):
        t = tab[tab["stream_name"] == NAMES[kind]].sort_values("thresh_scale")
        x = np.log2(t["thresh_scale"])
        axes[0].plot(x, t["observed rate"], color=c, linewidth=2, marker="o", markersize=5, label=NAMES[kind])
        axes[1].plot(x, t["95th pct |err| %"], color=c, linewidth=2, marker="o", markersize=5, label=NAMES[kind])
    axes[0].axhline(0.1, color=REF, linestyle="--", linewidth=1.2)
    axes[0].text(-8, 0.105, "δ = 0.1", color=MUTED, fontsize=8.5, va="bottom")
    axes[1].axhline(20, color=REF, linestyle="--", linewidth=1.2)
    axes[1].text(-8, 20.5, "ε = 20%", color=MUTED, fontsize=8.5, va="bottom")
    ticks = [int(round(math.log2(s))) for s in E2_SCALES]
    for ax in axes:
        ax.set_xticks(ticks)
        ax.set_xticklabels(["1" if t == 0 else f"1/{2 ** -t}" for t in ticks])
        ax.set_xlabel("threshold scale c (paper's threshold × c)")
        ax.invert_xaxis()
    axes[0].set_ylabel("share of runs failing the guarantee")
    axes[0].set_ylim(bottom=0)
    axes[1].set_ylabel("95th percentile |error| (%)")
    axes[1].set_ylim(bottom=0)
    axes[0].legend(loc="upper left", fontsize=8.5)
    fig.suptitle("E2: the threshold can be about 32× smaller and still keep failures below δ = 0.1", x=0.01, ha="left",
                 color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig("figures/e2_threshold.png")
    plt.close(fig)
    return tab


def e5():
    df = load("e5")
    df["order"] = df["stream_params"].map(lambda s: json.loads(s)["order"])
    tab = df.groupby(["thresh_scale", "order"]).apply(summarise, include_groups=False).reset_index()
    tab["order"] = pd.Categorical(tab["order"], E5_ORDERS)
    tab = tab.sort_values(["thresh_scale", "order"], ascending=[False, True])
    with open("results/summary_e5.md", "w") as f:
        f.write("# E5 — the same items in four orders (S3 Zipf, ε = 0.2, δ = 0.1, 2,000 seeds per row)\n\n"
                + md_table(tab.rename(columns={"thresh_scale": "scale c"})) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=False)
    for ax, c in zip(axes, (1.0, 1 / 16)):
        data = [df[(df["thresh_scale"] == c) & (df["order"] == o)]["signed"].dropna() * 100 for o in E5_ORDERS]
        bp = ax.boxplot(data, whis=(2.5, 97.5), showfliers=False, widths=0.5, patch_artist=True,
                        medianprops={"color": INK, "linewidth": 1.5})
        for b in bp["boxes"]:
            b.set(facecolor="#257de0", alpha=0.18, edgecolor="#257de0")
        for w in bp["whiskers"] + bp["caps"]:
            w.set(color="#257de0")
        ax.axhline(0, color=REF, linewidth=1)
        ax.set_xticks(range(1, 5), [ORDER_NAMES[o] for o in E5_ORDERS])
        ax.set_title("paper's threshold" if c == 1 else "threshold × 1/16")
        ax.set_ylabel("signed relative error (%)")
    fig.suptitle("E5: the stream's order does not change CVM's error (boxes: 25–75%, whiskers: 2.5–97.5%)",
                 x=0.01, ha="left", color=INK, fontsize=11.5, fontweight="bold")
    fig.tight_layout()
    fig.savefig("figures/e5_order.png")
    plt.close(fig)
    return tab


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    for name, fn in (("e1", e1), ("e2", e2), ("e5", e5)):
        if os.path.exists(f"results/{name}.csv"):
            fn()
            print("done", name)
