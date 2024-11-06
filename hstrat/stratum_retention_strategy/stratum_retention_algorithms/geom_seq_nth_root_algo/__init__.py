"""Maintain constant size complexity with recency-proportional strata spacing.

The approximate space-filling MRCA-recency-proportional resolution policy
imposes an O(1) limit on the number of retained strata and guarantees that
retained strata will be exponentially distributed with respect to ranks elapsed
since their deposit. MRCA rank estimate uncertainty scales in the worst case
scales as O(n) with respect to the greater number of strata deposited on either
column. However, with respect to estimating the rank of the MRCA when lineages
diverged any fixed number of generations ago, uncertainty scales as O(n^{1/k}).

Under the MRCA-recency-proportional resolution policy, the number of strata
retained (i.e., space complexity) scales as O(1) with respect to the number of
strata deposited.

Suppose k is specified as the policy's target precision k. Then, the first k
strata deposited will be retained. Subsequently, strata are retained so that
MRCA rank estimate uncertainty is less than or equal to s * (1 - n^(-1/k)) is
the number of strata deposited and s is the true number of ranks deposited
since the MRCA. As n goes to infinity, the number of strata retained fluctuates
below a hard upper limit of 4k + 2 (inclusive) strata. For larger target space
utilizations, number of strata retained appears generally less than twice the
target space utilization.

See Also
--------
geom_seq_nth_root_tapered_algo:
    For a predicate retention policy that achieves the same guarantees for
    resolution but retains a constant column size exactly equal to the hard
    upper limit on number of strata retained.
"""

from ...._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(__name__, __file__)
del lazy_attach_stub
