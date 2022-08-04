"""Stratum retention policies that specify which set of strata ranks that
should be retained in a hereditary stratigraphic column when the nth stratum is
deposited."""

from . import perfect_resolution_policy

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    'perfect_resolution_policy',
]
