"""
Must be defined in a separate file so that it is able to be imported
by the attach_stub function and loaded into the init. The module of this
list is laundered making it essentially defined therein.
"""

from . import (
    depth_proportional_resolution_algo,
    depth_proportional_resolution_tapered_algo,
    fixed_resolution_algo,
    geom_seq_nth_root_algo,
    geom_seq_nth_root_tapered_algo,
    nominal_resolution_algo,
    perfect_resolution_algo,
    pseudostochastic_algo,
    recency_proportional_resolution_algo,
    recency_proportional_resolution_curbed_algo,
    stochastic_algo,
)

provided_stratum_retention_algorithms = [
    depth_proportional_resolution_algo,
    depth_proportional_resolution_tapered_algo,
    fixed_resolution_algo,
    geom_seq_nth_root_algo,
    geom_seq_nth_root_tapered_algo,
    nominal_resolution_algo,
    perfect_resolution_algo,
    pseudostochastic_algo,
    recency_proportional_resolution_algo,
    recency_proportional_resolution_curbed_algo,
    stochastic_algo,
]
