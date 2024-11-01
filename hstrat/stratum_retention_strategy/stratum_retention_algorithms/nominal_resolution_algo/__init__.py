"""Retain as few strata as possible.

The nominal resolution policy only retains the most ancient (i.e., very
first) and most recent (i.e., last) strata. So, comparisons between two
columns under this policy will only be able to detect whether they share
any common ancestor and whether they are from the same organism (i.e., no
generations have elapsed since the MRCA). Thus, MRCA rank estimate
uncertainty scales as O(n) with respect to the greater number of strata deposited on either column.

Under the nominal resolution policy, the number of strata retained (i.e.,
space complexity) scales as O(1) with respect to the number of strata
deposited.
"""

from ...._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(__name__, __file__)
del lazy_attach_stub
