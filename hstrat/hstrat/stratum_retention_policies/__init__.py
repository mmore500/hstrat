"""Logic to control stratum retention within HereditaryStratigraphicColumn.

Stratum retention policies specify which strata ranks that should be retained ----- and which should be purged --- when the nth stratum is deposited.
"""

from . import (
    depth_proportional_resolution_policy,
    depth_proportional_resolution_tapered_policy,
    fixed_resolution_policy,
    geom_seq_nth_root_policy,
    geom_seq_nth_root_tapered_policy,
    nominal_resolution_policy,
    perfect_resolution_policy,
    pseudostochastic_policy,
    recency_proportional_resolution_policy,
    stochastic_policy,
)
from ._detail import UnsatisfiableParameterizationRequestError

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "UnsatisfiableParameterizationRequestError",
    "depth_proportional_resolution_policy",
    "depth_proportional_resolution_tapered_policy",
    "fixed_resolution_policy",
    "geom_seq_nth_root_policy",
    "geom_seq_nth_root_tapered_policy",
    "nominal_resolution_policy",
    "perfect_resolution_policy",
    "pseudostochastic_policy",
    "recency_proportional_resolution_policy",
    "stochastic_policy",
]

from ...helpers import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
