from .._detail import PolicyCouplerFactory
from .PolicySpec import PolicySpec
from ._enact.GenDropRanks import GenDropRanks
from ._invar.CalcMrcaUncertaintyAbsUpperBound import (
    CalcMrcaUncertaintyAbsUpperBound,
)
from ._invar.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
)
from ._invar.CalcMrcaUncertaintyAbsUpperBoundPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
)
from ._invar.CalcMrcaUncertaintyRelUpperBound import (
    CalcMrcaUncertaintyRelUpperBound,
)
from ._invar.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
)
from ._invar.CalcMrcaUncertaintyRelUpperBoundPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundPessimalRank,
)
from ._invar.CalcNumStrataRetainedUpperBound import (
    CalcNumStrataRetainedUpperBound,
)
from ._scry.CalcMrcaUncertaintyAbsExact import CalcMrcaUncertaintyAbsExact
from ._scry.CalcMrcaUncertaintyRelExact import CalcMrcaUncertaintyRelExact
from ._scry.CalcNumStrataRetainedExact import CalcNumStrataRetainedExact
from ._scry.CalcRankAtColumnIndex import CalcRankAtColumnIndex
from ._scry.IterRetainedRanks import IterRetainedRanks

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
