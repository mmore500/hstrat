"""Stratum retention policies that specify which set of strata ranks that
should be retained in a hereditary stratigraphic column when the nth stratum is
deposited."""

from . import depth_proportional_resolution_policy
from . import depth_proportional_resolution_tapered_policy
from . import fixed_resolution_policy
from . import geom_seq_nth_root_policy
from . import nominal_resolution_policy
from . import perfect_resolution_policy
from . import recency_proportional_resolution_policy

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    'depth_proportional_resolution_policy',
    'depth_proportional_resolution_tapered_policy',
    'fixed_resolution_policy',
    'geom_seq_nth_root_policy',
    'nominal_resolution_policy',
    'perfect_resolution_policy',
    'recency_proportional_resolution_policy',
]
