"""Retain all strata to ensure perfect resolution for MRCA estimation.

The perfect resolution policy retains all strata. So, comparisons between
two columns under this policy will detect MRCA rank with zero
uncertainty. So, MRCA rank estimate uncertainty scales as O(1) with respect
to the greater number of strata deposited on either column.

Under the perfect resolution policy, the number of strata retained (i.e.,
space complexity) scales as O(n) with respect to the number of strata
deposited.
"""

from ...._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(__name__, __file__)
del lazy_attach_stub
