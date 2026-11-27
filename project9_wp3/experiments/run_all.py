"""Run E1, E2 and E5 into results/*.csv (resumable: re-running only fills in missing seeds).

    python -m experiments.run_all            # all three
    python -m experiments.run_all E1         # one experiment
"""
import sys

from experiments import configs
from experiments.run import run_configs

EXPS = {"E1": configs.e1, "E2": configs.e2, "E5": configs.e5}

if __name__ == "__main__":
    for name in (sys.argv[1:] or EXPS):
        run_configs(EXPS[name](), f"results/{name.lower()}.csv")
