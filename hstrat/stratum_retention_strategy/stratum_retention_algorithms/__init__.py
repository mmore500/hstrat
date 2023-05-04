"""Logic to control stratum retention within HereditaryStratigraphicColumn.

Stratum retention policies specify which strata ranks that should be retained ----- and which should be purged --- when the nth stratum is deposited.
Stratum retention algorithms can be parameterized to yield a policy.
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
from ._detail import UnsatisfiableParameterizationRequestError

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
    stochastic_algo,
]

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

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
