from .._detail import PolicyCouplerFactory

from . import CalcMrcaUncertaintyAbsExact
from . import CalcMrcaUncertaintyRelExact
from . import CalcNumStrataRetainedExact
from . import CalcMrcaUncertaintyAbsUpperBound
from . import CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank
from . import CalcMrcaUncertaintyAbsUpperBoundPessimalRank
from . import CalcMrcaUncertaintyRelUpperBound
from . import CalcMrcaUncertaintyRelUpperBoundAtPessimalRank
from . import CalcMrcaUncertaintyRelUpperBoundPessimalRank
from . import CalcNumStrataRetainedUpperBound
from . import CalcRankAtColumnIndex
from . import GenDropRanks
from . import IterRetainedRanks
from . import PolicySpec

Policy = PolicyCouplerFactory(
    policy_spec_t=PolicySpec,
    # enactment
    gen_drop_ranks_ftor_t=GenDropRanks,
    # invariants
    calc_mrca_uncertainty_abs_upper_bound_ftor_t\
        =CalcMrcaUncertaintyAbsUpperBound,
    calc_mrca_uncertainty_abs_upper_bound_at_pessimal_rank_ftor_t\
        =CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
    calc_mrca_uncertainty_abs_upper_bound_pessimal_rank_ftor_t\
        =CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
    calc_mrca_uncertainty_rel_upper_bound_ftor_t\
        =CalcMrcaUncertaintyRelUpperBound,
    calc_mrca_uncertainty_rel_upper_bound_at_pessimal_rank_ftor_t\
        =CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
    calc_mrca_uncertainty_rel_upper_bound_pessimal_rank_ftor_t\
        =CalcMrcaUncertaintyRelUpperBoundPessimalRank,
    calc_num_strata_retained_upper_bound_ftor_t\
        =CalcNumStrataRetainedUpperBound,
    # scrying
    calc_mrca_uncertainty_abs_exact_ftor_t=CalcMrcaUncertaintyAbsExact,
    calc_mrca_uncertainty_rel_exact_ftor_t=CalcMrcaUncertaintyRelExact,
    calc_num_strata_retained_exact_ftor_t=CalcNumStrataRetainedExact,
    calc_rank_at_column_index_ftor_t=CalcRankAtColumnIndex,
    iter_retained_ranks_ftor_t=IterRetainedRanks,
)

# gloss away PolicyCoupler implementation details
Policy.__name__ = 'Policy'
Policy.__qualname__ = 'Policy'
Policy.__module__ = __name__
