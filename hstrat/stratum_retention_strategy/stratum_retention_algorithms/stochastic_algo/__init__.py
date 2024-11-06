"""Retain strata probabilistically in a nondeterministic manner.

It would be a poor choice to use in practice because mismatches between the
particular ranks that each column happens to have strata for will degrade
the effectiveness of comparisons between columns. Rather, it is included in
the library as an edge case for testing purposes. Worst-case MRCA rank estimate uncertainty scales as O(n) with respect to the greater number of strata deposited on either column being compared.

Under the stochastic resolution policy, the worst and average case number
of strata retained (i.e., space complexity) scales as O(n) with respect to
the number of strata deposited.

This policy implementation that the most ancient and most recent strata will
always be retained. For the secondmost recently deposited sratum, a
pseudorandom coin flip is performed. Depending on the outcome of that coin
flip, the stratum is either immediately purged or retained permanently.
"""
from ...._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(__name__, __file__)
del lazy_attach_stub
