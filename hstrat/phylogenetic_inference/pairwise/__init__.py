"""Functions to infer phylogenetic history between two extant hstrat
columns."""

from ._calc_rank_of_earliest_detectable_mrca_between import (
    calc_rank_of_earliest_detectable_mrca_between,
)
from ._calc_rank_of_mrca_bounds_between import calc_rank_of_mrca_bounds_between
from ._calc_rank_of_mrca_bounds_provided_confidence_level import (
    calc_rank_of_mrca_bounds_provided_confidence_level,
)
from ._calc_rank_of_mrca_uncertainty_between import (
    calc_rank_of_mrca_uncertainty_between,
)
from ._calc_ranks_since_earliest_detectable_mrca_with import (
    calc_ranks_since_earliest_detectable_mrca_with,
)
from ._calc_ranks_since_mrca_bounds_provided_confidence_level import (
    calc_ranks_since_mrca_bounds_provided_confidence_level,
)
from ._calc_ranks_since_mrca_bounds_with import (
    calc_ranks_since_mrca_bounds_with,
)
from ._calc_ranks_since_mrca_uncertainty_with import (
    calc_ranks_since_mrca_uncertainty_with,
)
from ._does_definitively_have_no_common_ancestor import (
    does_definitively_have_no_common_ancestor,
)
from ._does_have_any_common_ancestor import does_have_any_common_ancestor

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "calc_rank_of_earliest_detectable_mrca_between",
    "calc_rank_of_mrca_bounds_between",
    "calc_rank_of_mrca_bounds_provided_confidence_level",
    "calc_rank_of_mrca_uncertainty_between",
    "calc_ranks_since_earliest_detectable_mrca_with",
    "calc_ranks_since_mrca_bounds_with",
    "calc_ranks_since_mrca_bounds_provided_confidence_level",
    "calc_ranks_since_mrca_uncertainty_with",
    "does_definitively_have_no_common_ancestor",
    "does_have_any_common_ancestor",
]

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
