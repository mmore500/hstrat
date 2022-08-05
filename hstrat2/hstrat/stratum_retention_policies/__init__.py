"""Stratum retention policies that specify which set of strata ranks that
should be retained in a hereditary stratigraphic column when the nth stratum is
deposited."""

from . import depth_proportional_resolution_policy
from . import fixed_resolution_policy
from . import nominal_resolution_policy
from . import perfect_resolution_policy

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    'depth_proportional_resolution_policy',
    'fixed_resolution_policy',
    'nominal_resolution_policy',
    'perfect_resolution_policy',
]
