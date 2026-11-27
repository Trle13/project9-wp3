"""Which estimator class belongs to which name. WP2/WP4 add their classes here."""
from estimators.cvm_reference import CVM
from estimators.exact import ExactSet

ESTIMATORS = {
    "cvm": CVM,          # replace with WP2's official class when it is ready
    "exact": ExactSet,   # replace with WP4's version when it is ready
    # "hll": HyperLogLog,   (WP4)
    # "kmv": KMV,           (WP4)
}
