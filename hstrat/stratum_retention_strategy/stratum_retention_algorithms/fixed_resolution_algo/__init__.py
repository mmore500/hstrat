"""Accept linear size complexity to maintain fixed spacing between strata.

The fixed resolution policy ensures estimates of MRCA rank will have
uncertainty bounds less than or equal a fixed, absolute user-specified cap
that is independent of the number of strata deposited on either column.
Thus, MRCA rank estimate uncertainty scales as O(1) with respect to the
greater number of strata deposited on either column.

Under the fixed resolution policy, the number of strata retained (i.e.,
space complexity) scales as O(n) with respect to the number of strata
deposited.
"""

from ...._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(__name__, __file__)
del lazy_attach_stub
