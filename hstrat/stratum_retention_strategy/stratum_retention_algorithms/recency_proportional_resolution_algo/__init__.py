r"""Provide log space complexity and recency-proportional strata spacing.

The MRCA-recency-proportional resolution policy ensures estimates of MRCA
rank will have uncertainty bounds less than or equal to a user-specified
proportion of the actual number of generations elapsed since the MRCA and the
deepest of the compared columns. MRCA rank estimate uncertainty scales in the
worst case scales as O(n) with respect to the greater number of strata
deposited on either column. However, with respect to estimating the rank of the
MRCA when lineages diverged any fixed number of generations ago, uncertainty
scales as O(1).

Under the MRCA-recency-proportional resolution policy, the number of strata
retained (i.e., space complexity) scales as O(log(n)) with respect to the
number of strata deposited.


This functor's retention policy implementation guarantees that columns will
retain appropriate strata so that for any two columns with m and n strata
deposited, the rank of the most recent common ancestor at rank k can be
determined with uncertainty of at most

    bound = floor(
        max(m - k, n - k)
        / recency_proportional_resolution
    )

ranks.

How does the predicate work and how does it guarantee this resolution?

To begin, let's consider setting up just the *first* rank of the stratum after
the root ancestor we will retain.

root ancestor                                     extant individual
|                                                                 |
|                    num_strata_deposited                         |
| ___________________________/\_________________________________  |
|/                                                               \|
|-------------------|#############################################|
 \_______  ________/|\____________________  ______________________/
         \/         |                     \/
   max_uncertainty  |            worst_case_mrca_depth
                    |
                    proposed retention rank

To provide guaranteed resolution, max_uncertainty must be leq than

    worst_case_mrca_depth // guaranteed_resolution

So, to find the largest permissible max_uncertainty we must solve

    max_uncertainty = worst_case_mrca_depth // guaranteed_resolution

By construction we have

    worst_case_mrca_depth = num_strata_deposited - max_uncertainty

Substituting into the above expression gives

    max_uncertainty
    = (num_strata_deposited - max_uncertainty) // guaranteed_resolution

Solving for max_uncertainty yields

    max_uncertainty
    = num_strata_deposited // (guaranteed_resolution + 1)

We now have an upper bound for the rank of the first stratum rank we must
retain. We can repeat this process recursively to select ranks that give
adequate resolution proportional to worst_case_mrca_depth.

However, we must guarantee that thes ranks are actually available for us to
retain (i.e., it hasn't been purged out of the column at a previous time point
as the column was grown by successive deposition). We will do this by picking
the rank that is the highest power of 2 less than or equal to our bound. If we
repeat this procedure as we recurse, we are guaranteed that this rank will have
been preserved across all previous timepoints.

This is because a partial sum sequence where all elements are powers of 2 and
elements in the sequence are will include all multiples of powers of 2 greater
than or equal to the first element that are less than or equal to the sum of
the entire sequence.

An example is the best way to convince yourself. Thinking analogously in base
10,

    100 + 10... + 1...

the partial sums of any sequence of this form will always include all multiples
of powers of 100, 1000, etc. that are less than or equal to the sum of the
entire sequence.

In our application, partial sums represent retained ranks. So, all ranks that
are perfect powers of 2 measuring from the root ancestor will have been
retained after being deposited. This property generalizes recursively.
"""

from ._Policy import Policy
from ._PolicySpec import PolicySpec
from ._enact._GenDropRanks import GenDropRanks
from ._enact._GenDropRanks_ import impls as _GenDropRanks_impls
from ._invar._CalcMrcaUncertaintyAbsUpperBound import (
    CalcMrcaUncertaintyAbsUpperBound,
)
from ._invar._CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
)
from ._invar._CalcMrcaUncertaintyAbsUpperBoundPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
)
from ._invar._CalcMrcaUncertaintyRelUpperBound import (
    CalcMrcaUncertaintyRelUpperBound,
)
from ._invar._CalcMrcaUncertaintyRelUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
)
from ._invar._CalcMrcaUncertaintyRelUpperBoundPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundPessimalRank,
)
from ._invar._CalcNumStrataRetainedUpperBound import (
    CalcNumStrataRetainedUpperBound,
)
from ._scry._CalcMrcaUncertaintyAbsExact import CalcMrcaUncertaintyAbsExact
from ._scry._CalcMrcaUncertaintyRelExact import CalcMrcaUncertaintyRelExact
from ._scry._CalcNumStrataRetainedExact import CalcNumStrataRetainedExact
from ._scry._CalcRankAtColumnIndex import CalcRankAtColumnIndex
from ._scry._IterRetainedRanks import IterRetainedRanks

__all__ = [
    "CalcMrcaUncertaintyAbsExact",
    "CalcMrcaUncertaintyAbsUpperBound",
    "CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank",
    "CalcMrcaUncertaintyAbsUpperBoundPessimalRank",
    "CalcMrcaUncertaintyRelExact",
    "CalcMrcaUncertaintyRelUpperBound",
    "CalcMrcaUncertaintyRelUpperBoundAtPessimalRank",
    "CalcMrcaUncertaintyRelUpperBoundPessimalRank",
    "CalcNumStrataRetainedExact",
    "CalcNumStrataRetainedUpperBound",
    "CalcRankAtColumnIndex",
    "GenDropRanks",
    "_GenDropRanks_impls",
    "IterRetainedRanks",
    "Policy",
    "PolicySpec",
]

from ...._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
