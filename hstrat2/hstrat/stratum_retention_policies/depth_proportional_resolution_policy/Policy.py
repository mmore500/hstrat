from .._detail import PolicyCouplerFactory

from . import CalcMrcaUncertaintyExact
from . import CalcNumStrataRetainedExact
from . import CalcMrcaUncertaintyUpperBound
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
    calc_mrca_uncertainty_upper_bound_ftor_t\
        =CalcMrcaUncertaintyUpperBound,
    calc_num_strata_retained_upper_bound_ftor_t\
        =CalcNumStrataRetainedUpperBound,
    # scrying
    calc_mrca_uncertainty_exact_ftor_t=CalcMrcaUncertaintyExact,
    calc_num_strata_retained_exact_ftor_t=CalcNumStrataRetainedExact,
    calc_rank_at_column_index_ftor_t=CalcRankAtColumnIndex,
    iter_retained_ranks_ftor_t=IterRetainedRanks,
)

# gloss away PolicyCoupler implementation details
Policy.__name__ = 'Policy'
Policy.__qualname__ = 'Policy'
Policy.__module__ = __name__
