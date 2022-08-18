"""Functors that implement stratum retention policies by specifying
the set of strata ranks that should be pruned from a hereditary
stratigraphic column when the nth stratum is deposited."""

from .StratumRetentionCondemnerFromPredicate import (
    StratumRetentionCondemnerFromPredicate,
)

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "StratumRetentionCondemnerFromPredicate",
]
