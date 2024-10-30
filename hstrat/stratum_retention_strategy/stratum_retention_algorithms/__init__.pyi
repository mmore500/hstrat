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
from ._detail import UnsatisfiableParameterizationRequestError
from ._provided_stratum_retention_algorithms import (
    provided_stratum_retention_algorithms,
)

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "UnsatisfiableParameterizationRequestError",
    "depth_proportional_resolution_algo",
    "depth_proportional_resolution_tapered_algo",
    "fixed_resolution_algo",
    "geom_seq_nth_root_algo",
    "geom_seq_nth_root_tapered_algo",
    "nominal_resolution_algo",
    "perfect_resolution_algo",
    "provided_stratum_retention_algorithms",
    "pseudostochastic_algo",
    "recency_proportional_resolution_algo",
    "recency_proportional_resolution_curbed_algo",
    "stochastic_algo",
]
