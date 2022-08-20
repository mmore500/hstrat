from .._detail import PolicyCouplerFactory
from ._PolicySpec import PolicySpec
from ._enact._GenDropRanks import GenDropRanks
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

Policy = PolicyCouplerFactory(
    policy_spec_t=PolicySpec,
    # enactment
    gen_drop_ranks_ftor_t=GenDropRanks,
    # invariants
    calc_mrca_uncertainty_abs_upper_bound_ftor_t=CalcMrcaUncertaintyAbsUpperBound,
    calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor_t=CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
    calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor_t=CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
    calc_mrca_uncertainty_rel_upper_bound_ftor_t=CalcMrcaUncertaintyRelUpperBound,
    calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor_t=CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
    calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor_t=CalcMrcaUncertaintyRelUpperBoundPessimalRank,
    calc_num_strata_retained_upper_bound_ftor_t=CalcNumStrataRetainedUpperBound,
    # scrying
    calc_mrca_uncertainty_abs_exact_ftor_t=CalcMrcaUncertaintyAbsExact,
    calc_mrca_uncertainty_rel_exact_ftor_t=CalcMrcaUncertaintyRelExact,
    calc_num_strata_retained_exact_ftor_t=CalcNumStrataRetainedExact,
    calc_rank_at_column_index_ftor_t=CalcRankAtColumnIndex,
    iter_retained_ranks_ftor_t=IterRetainedRanks,
)

# gloss away PolicyCoupler implementation details
Policy.__name__ = "Policy"
Policy.__qualname__ = "Policy"
Policy.__module__ = __name__
