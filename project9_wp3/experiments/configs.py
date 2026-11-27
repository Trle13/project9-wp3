"""Experiment definitions (E1, E2, E5 run now; E3/E4 wait for WP4's baselines and the real logs)."""
M = 10 ** 5
SEEDS = 2000
STREAMS = {  # name -> (kind, params)
    "S1 uniform": ("uniform", {"n_values": M}),
    "S2 all-distinct": ("all_distinct", {}),
    "S3 Zipf s=1.1": ("zipf", {"s": 1.1, "n_values": 10 * M}),
}


def e1():
    """E1: does CVM meet (eps, delta)?  3 streams x eps {0.2,0.3,0.5} x delta {0.01,0.1}."""
    return [{"experiment": "E1", "estimator": "cvm", "est_params": {"eps": e, "delta": d},
             "stream": kind, "stream_params": sp, "m": M, "stream_seed": 0, "n_seeds": SEEDS}
            for kind, sp in STREAMS.values() for e in (0.2, 0.3, 0.5) for d in (0.01, 0.1)]


E2_SCALES = [1, 1 / 2, 1 / 4, 1 / 8, 1 / 16, 1 / 32, 1 / 64, 1 / 128, 1 / 256]


def e2():
    """E2: how conservative is the threshold?  eps=0.2, delta=0.1, threshold x c."""
    return [{"experiment": "E2", "estimator": "cvm", "est_params": {"eps": 0.2, "delta": 0.1, "thresh_scale": c},
             "stream": kind, "stream_params": sp, "m": M, "stream_seed": 0, "n_seeds": SEEDS}
            for kind, sp in STREAMS.values() for c in E2_SCALES]


E5_ORDERS = ["random", "sorted", "bursts", "new_last"]


def e5():
    """E5: does the order of the stream matter?  S3's items in 4 orders, full and 1/16 threshold."""
    return [{"experiment": "E5", "estimator": "cvm", "est_params": {"eps": 0.2, "delta": 0.1, "thresh_scale": c},
             "stream": "reordered", "stream_params": {"base": "zipf", "s": 1.1, "n_values": 10 * M, "order": o},
             "m": M, "stream_seed": 0, "n_seeds": SEEDS}
            for c in (1, 1 / 16) for o in E5_ORDERS]
